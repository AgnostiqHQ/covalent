# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Dispatch DataBase script."""

import copy
from datetime import datetime

import networkx as nx

import covalent.executor as covalent_executor
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
    # TODO: This is an outdated method

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

        metadata["hooks"]["deps"] = encode_dict(metadata["hooks"]["deps"])
        call_before = metadata["hooks"]["call_before"]
        call_after = metadata["hooks"]["call_after"]
        for i, dep in enumerate(call_before):
            call_before[i] = str(dep)

        for i, dep in enumerate(call_after):
            call_after[i] = str(dep)

        metadata["hooks"]["call_before"] = call_before
        metadata["hooks"]["call_after"] = call_after

    except (KeyError, AttributeError) as ex:
        app_log.debug(f"Exception when trying to extract metadata: {ex}")

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
