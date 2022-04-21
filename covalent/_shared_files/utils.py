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

"""General utils for Covalent."""

import inspect
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable, Dict, Set, Tuple

import networkx as nx
import simplejson

import covalent.executor as covalent_executor

from . import logger
from .util_classes import Status

app_log = logger.app_log
log_stack_info = logger.log_stack_info

if TYPE_CHECKING:
    from .._results_manager.result import Result


def get_timedelta(time_limit: str) -> timedelta:
    """
    Get timedelta from a compatible time limit string passed to the lattice/electron decorator.

    Args:
        time_limit: The time limit string.
    Returns:
        timedelta: The `datetime.timedelta` object.
    """

    days, hours, minutes, seconds = time_limit.split("-")[0], *time_limit.split("-")[1].split(":")
    return timedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
    )


def reformat(t: int) -> str:
    """
    Reformat an integer to a readable time-like string. For example, if t = 1, return "01".

     Args:
         t: The integer to reformat.

     Returns:
         ref_string: The reformatted string.
    """

    return f"0{t}" if len(str(t)) == 1 else str(t)


def get_time(time_delta: timedelta) -> str:
    """
    Get a compatible time string from a timedelta object.

    Args:
        time_delta: The timedelta object.
    Returns:
        time_string: The compatible reformatted time string.
    """

    days = time_delta.days
    hours = reformat(time_delta.seconds // 3600)
    minutes = reformat((time_delta.seconds // 60) % 60)
    seconds = reformat(time_delta.seconds % 60)
    return f"{days}-{hours}:{minutes}:{seconds}"


def get_serialized_function_str(function):
    """
    Generates a string representation of a function definition
    including the decorators on it.

    Args:
        function: The function whose definition is to be convert to a string.

    Returns:
        function_str: The string representation of the function definition.
    """

    input_function = function
    # If a Lattice or electron object was passed as the function input, we need the
    # underlying function describing the lattice.
    while hasattr(input_function, "workflow_function"):
        input_function = input_function.workflow_function

    try:
        # function_str is the string representation of one function, with decorators, if any.
        function_str = inspect.getsource(input_function)
    except Exception:
        function_str = f"# {function.__name__} was not inspectable"

    return function_str + "\n\n"


def get_imports(func: Callable) -> Tuple[str, Set[str]]:
    """
    Given an input workflow function, find the imports that were used, and determine
        which ones are Covalent-related.

    Args:
        func: workflow function.

    Returns:
        A tuple consisting of a string of import statements and a set of names that
            Covalent-related modules have been imported as.
    """

    imports_str = ""
    cova_imports = set()
    for i, j in func.__globals__.items():
        if inspect.ismodule(j) or (
            inspect.isfunction(j) and j.__name__ in ["lattice", "electron"]
        ):
            if j.__name__ == i:
                import_line = f"import {j.__name__}\n"
            else:
                import_line = f"import {j.__name__} as {i}\n"

            if j.__name__ in ["covalent", "lattice", "electron"]:
                import_line = f"# {import_line}"
                cova_imports.add(i)

            imports_str += import_line

    return imports_str, cova_imports


def required_params_passed(func: Callable, kwargs: Dict) -> bool:  # pragma: no cover
    """
    DEPRECATED: Check to see that values for all parameters without default values have been passed.

    Args:
        func: Callable function.
        kwargs: Parameter list with passed values.

    Returns:
        status: Whether all the parameters required for the callable function has been passed.
    """

    required_arg_set = set({})
    sig = inspect.signature(func)
    for param in sig.parameters.values():
        if param.default is param.empty:
            required_arg_set.add(str(param))

    return required_arg_set.issubset(set(kwargs.keys()))


def get_named_params(func, args, kwargs):
    ordered_params_dict = inspect.signature(func).parameters
    named_args = {}
    named_kwargs = {}

    for ind, parameter_dict in enumerate(ordered_params_dict.items()):

        param_name, param = parameter_dict

        if param.kind in [param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD]:
            if param_name in kwargs:
                named_kwargs[param_name] = kwargs[param_name]
            elif ind < len(args):
                named_args[param_name] = args[ind]
        elif param.kind == param.VAR_POSITIONAL:
            for i in range(ind, len(args)):
                named_args[f"arg[{i}]"] = args[i]

        elif param.kind in [param.KEYWORD_ONLY, param.VAR_KEYWORD]:
            for key, value in kwargs.items():
                if key != param_name:
                    named_kwargs[key] = value

    return (named_args, named_kwargs)


def extract_graph_node(node):
    # avoid mutating original node
    node = node.copy()

    # doc string
    f = node.get("function")
    if f is not None:
        node["doc"] = f.func_doc

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
    return {k: str(v) for (k, v) in d.items()} if isinstance(d, dict) else d


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


def encode_result(result_obj: "Result"):

    transport_graph = result_obj.transport_graph

    result_dict = {
        "dispatch_id": result_obj.dispatch_id,
        "status": result_obj.status,
        "result": result_obj.result,
        "start_time": result_obj.start_time,
        "end_time": result_obj.end_time,
        "results_dir": result_obj.results_dir,
        "error": result_obj.error,
        "lattice": {
            "function_string": result_obj.workflow_function_string,
            "doc": result_obj.lattice_doc,
            "name": result_obj.lattice_name,
            "inputs": encode_dict(result_obj.inputs),
            "metadata": extract_metadata(transport_graph.lattice_metadata),
        },
        "graph": extract_graph(transport_graph._graph),
    }

    jsonified_result = simplejson.dumps(result_dict, default=result_encoder, ignore_nan=True)

    return jsonified_result
