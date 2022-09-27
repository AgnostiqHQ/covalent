# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Dispatch DataBase script."""

import copy
from datetime import datetime

import networkx as nx
import simplejson

import covalent.executor as covalent_executor
from covalent._data_store import DataStore
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import Status

app_log = logger.app_log
log_stack_info = logger.log_stack_info
# DB Schema:
# TABLE dispatches
# * dispatch_id text primary key
# * result_dict text ; json-serialied dictionary representation of Result

# TODO: Move these to a common utils module


def extract_graph_node(node):
    # avoid mutating original node
    node = node.copy()

    # doc string
    f = node.get("function")
    if f is not None:
        node["doc"] = f.attrs["doc"]

    if "value" in node and node["value"] is not None:
        node["value"] = node["value"].object_string
    if "output" in node and node["output"] is not None:
        node["output"] = node["output"].object_string

    # metadata
    node["metadata"] = extract_metadata(node["metadata"])

    # prevent JSON encoding
    node["kwargs"] = encode_dict(node.get("kwargs"))

    # remove unused fields
    node.pop("function", None)
    node.pop("node_name", None)

    return node


def extract_metadata(metadata: dict):
    try:
        # avoid mutating original metadata
        metadata = copy.deepcopy(metadata)

        name = metadata["executor"]
        app_log.debug(f"Getting executor {name}")
        executor = covalent_executor._executor_manager.get_executor(name=name)

        if executor is not None:
            # extract attributes
            metadata["executor"] = encode_dict(executor.__dict__)
            if isinstance(name, str):
                metadata["executor_name"] = name
            else:
                metadata["executor_name"] = f"<{executor.__class__.__name__}>"

        metadata["deps"] = encode_dict(metadata["deps"])
        call_before = metadata["call_before"]
        call_after = metadata["call_after"]
        for i, dep in enumerate(call_before):
            call_before[i] = str(dep)

        for i, dep in enumerate(call_after):
            call_after[i] = str(dep)

        metadata["call_before"] = call_before
        metadata["call_after"] = call_after

    except (KeyError, AttributeError) as ex:
        app_log.error(f"Exception when trying to extract metadata: {ex}")

    return metadata


def encode_dict(d):
    """Avoid JSON encoding when python str() suffices"""
    if not isinstance(d, dict):
        return d
    return {k: str(v) for (k, v) in d.items()}


def extract_graph(graph):
    graph = nx.json_graph.node_link_data(graph)
    nodes = list(map(extract_graph_node, graph["nodes"]))
    return {
        "nodes": nodes,
        "links": graph["links"],
    }


def result_encoder(obj):
    if isinstance(obj, Status):
        return obj.STATUS
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def encode_result(result_obj):
    lattice = result_obj.lattice

    result_string = result_obj.encoded_result.json
    if not result_string:
        result_string = result_obj.encoded_result.object_string

    named_args = {k: v.object_string for k, v in lattice.named_args.items()}
    named_kwargs = {k: v.object_string for k, v in lattice.named_kwargs.items()}
    result_dict = {
        "dispatch_id": result_obj.dispatch_id,
        "status": result_obj.status,
        "result": result_string,
        "start_time": result_obj.start_time,
        "end_time": result_obj.end_time,
        "results_dir": result_obj.results_dir,
        "error": result_obj.error,
        "lattice": {
            "function_string": lattice.workflow_function_string,
            "doc": lattice.__doc__,
            "name": lattice.__name__,
            "inputs": encode_dict({**named_args, **named_kwargs}),
            "metadata": extract_metadata(lattice.metadata),
        },
        "graph": extract_graph(result_obj.lattice.transport_graph._graph),
    }

    jsonified_result = simplejson.dumps(result_dict, default=result_encoder, ignore_nan=True)

    return jsonified_result


class DispatchDB:
    """
    Wrapper for the database of workflows.
    """

    def __init__(self, dbpath: str = None) -> None:
        if dbpath:
            self._dbpath = dbpath
        else:
            self._dbpath = get_config("user_interface.dispatch_db")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def _get_data_store(self, initialize_db: bool = False) -> DataStore:
        """Return the DataStore instance to write records."""

        return DataStore(db_URL=f"sqlite+pysqlite:///{self._dbpath}", initialize_db=initialize_db)
