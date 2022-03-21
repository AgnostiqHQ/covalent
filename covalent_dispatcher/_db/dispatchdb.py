import json
import os
import sqlite3
from datetime import datetime
from typing import List, Tuple

import networkx as nx
import simplejson

import covalent.executor as covalent_executor
from covalent._results_manager.result import Result
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import Status
from covalent._shared_files.utils import get_named_params

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
        node["doc"] = f.get_deserialized().__doc__

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
        metadata = metadata.copy()

        name = metadata["executor"]
        executor = covalent_executor._executor_manager.get_executor(name=name)

        if executor is not None:
            # extract attributes
            metadata["executor"] = encode_dict(executor.__dict__)
            if isinstance(name, str):
                metadata["executor_name"] = name
            else:
                metadata["executor_name"] = f"<{executor.__class__.__name__}>"
    except (KeyError, AttributeError):
        pass

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
    ((named_args, named_kwargs),) = (
        get_named_params(lattice.workflow_function, lattice.args, lattice.kwargs),
    )
    result_dict = {
        "dispatch_id": result_obj.dispatch_id,
        "status": result_obj.status,
        "result": result_obj.result,
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

        # dispatch_id is the primary key

        # Initialize the db if necessary; sqlite3 raises
        # sqlite3.OperationalError if table already exists.
        self.conn = sqlite3.connect(self._dbpath)
        try:
            self.conn.execute(
                "CREATE TABLE dispatches \
                (dispatch_id text primary key, \
                result_dict text)"
            )
            self.conn.commit()
        except sqlite3.OperationalError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.conn.close()

        return False

    def get(self, dispatch_ids: [] = []) -> List[Tuple[str, str]]:
        """
        Retrieve workflows with the given dispatch ids.

        Args:
            dispatch_ids: A list of dispatch ids for the sought-after workflows.

        Returns:
            A list of pairs (dispatch_id, [jsonified result dictionary]).
        """
        if len(dispatch_ids) > 0:
            placeholders = "({})".format(", ".join(["?" for i in dispatch_ids]))
            sql = (
                "SELECT * FROM dispatches WHERE \
            dispatch_id in "
                + placeholders
            )

            res = self.conn.execute(sql, dispatch_ids).fetchall()

        else:
            sql = "SELECT * FROM dispatches"

            res = self.conn.execute(sql).fetchall()

        return res

    def upsert(self, dispatch_id: str, result_obj: Result) -> None:
        """
        Insert or update the record with the given dispatch_id.

        Args:
            dispatch_id: The workflow's dispatch_id.
            result_obj: The Result object for the workflow.

        The Result is turned into a dictionary and stored as json.
        """

        jsonified_result = encode_result(result_obj)

        try:
            sql = "INSERT INTO dispatches (dispatch_id, result_dict) VALUES (?, ?)"
            self.conn.execute(sql, (dispatch_id, jsonified_result))
            self.conn.commit()

        except sqlite3.IntegrityError:
            sql = "UPDATE dispatches SET result_dict = ? WHERE dispatch_id = ?"
            self.conn.execute(sql, (jsonified_result, dispatch_id))
            self.conn.commit()

        # sql = "INSERT INTO dispatches (dispatch_id, result_dict) VALUES (?, ?) \
        # ON CONFLICT (dispatch_id) DO UPDATE SET result_dict = excluded.result_dict"

        # self.conn.execute(sql, (dispatch_id, jsonified_result))

    def delete(self, dispatch_ids: []) -> None:
        """
        Delete records with the given dispatch ids.

        Args:
            dispatch_ids: A list of dispatch ids
        """
        placeholders = "({})".format(", ".join(["?" for i in dispatch_ids]))
        sql = "DELETE FROM dispatches WHERE dispatch_id in " + placeholders

        self.conn.execute(sql, dispatch_ids)
        self.conn.commit()
