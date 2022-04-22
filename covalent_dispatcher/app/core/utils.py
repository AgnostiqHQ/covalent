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

"""Utility functions for the Dispatcher microservice."""

import os
import sys
from datetime import datetime, timezone
from io import BytesIO
from multiprocessing import Queue as MPQ
from queue import Empty
from typing import Any, Dict, List, Tuple

import cloudpickle as pickle
import requests
from app.core.dispatcher_logger import logger
from app.core.get_svc_uri import DispatcherURI, ResultsURI, RunnerURI, UIBackendURI
from dotenv import load_dotenv

from covalent._results_manager import Result
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import (
    attr_prefix,
    electron_dict_prefix,
    electron_list_prefix,
    generator_prefix,
    parameter_prefix,
    prefix_separator,
    sublattice_prefix,
    subscript_prefix,
)
from covalent._workflow.lattice import Lattice

load_dotenv()


BASE_URI = os.environ.get("BASE_URI")


def is_empty(mp_queue: MPQ):
    """The underlying assumption is that mpq contains only one element at any given time."""

    try:
        elem = mp_queue.get(timeout=1)
    except Empty:
        mp_queue.put(None)
        return True

    status = elem is None
    mp_queue.put(elem)
    return status


def preprocess_transport_graph(task_id: int, task_name: str, result_obj: Result) -> Result:
    """Ensure that the execution status of the task nodes in the transport graph are initialized
    properly."""

    is_executable_node = True

    if task_name.startswith((subscript_prefix, generator_prefix, parameter_prefix, attr_prefix)):
        if task_name.startswith(parameter_prefix):
            output = result_obj.transport_graph.get_node_value(task_id, "value")

        else:
            parent = result_obj.transport_graph.get_dependencies(task_id)[0]
            output = result_obj._get_node_output(parent)

            if task_name.startswith(attr_prefix):
                attr = result_obj.transport_graph.get_node_value(task_id, "attribute_name")
                output = getattr(output, attr)
            else:
                key = result_obj.transport_graph.get_node_value(task_id, "key")

                if output is None:
                    print(f"Failed task name: {task_name}", file=sys.stderr)
                output = output[key]

        result_obj._update_node(
            node_id=task_id,
            node_name=f"{task_name}({task_id})",
            start_time=datetime.now(timezone.utc),
            end_time=datetime.now(timezone.utc),
            status=Result.COMPLETED,
            output=output,
        )

        is_executable_node = False

    return result_obj, is_executable_node


def _post_process(lattice: Lattice, task_outputs: Dict) -> Any:
    """
    Post processing function to be called after the lattice execution.
    This takes care of executing statements that were not an electron
    but were inside the lattice's function. It also replaces any calls
    to an electron with the result of that electron execution, hence
    preventing a local execution of electron's function.

    Note: Here `node_outputs` is used instead of `electron_outputs`
    since an electron can be called multiple times with possibly different
    arguments, but every time it's called, it will be executed as a separate node.
    Thus, output of every node is used.

    Args:
        lattice: Lattice object that was dispatched.
        task_outputs: Dictionary containing the output of all the tasks.

    Returns:
        result: The result of the lattice function.
    """

    ordered_task_outputs = [
        val
        for key, val in task_outputs.items()
        if not key.startswith(prefix_separator) or key.startswith(sublattice_prefix)
    ]

    with active_lattice_manager.claim(lattice):
        lattice.post_processing = True
        lattice.electron_outputs = ordered_task_outputs
        result = lattice.workflow_function(*lattice.args, **lattice.kwargs)
        lattice.post_processing = False
        return result


def get_task_inputs(task_id: int, node_name: str, result_obj: Result) -> Dict:
    """
    Return the required inputs for a task execution.
    This makes sure that any node with child nodes isn't executed twice and fetches the
    result of parent node to use as input for the child node.

    Args:
        task_id: Node id of this task in the transport graph.
        node_name: Name of the node.
        result_obj: Result object to be used to update and store execution related
                       info including the results.

    Returns:
        inputs: Input dictionary to be passed to the task containing args, kwargs,
                and any parent node execution results if present.
    """

    if node_name.startswith(electron_list_prefix):
        values = [
            result_obj._get_node_output(parent)
            for parent in result_obj.transport_graph.get_dependencies(task_id)
        ]
        task_inputs = {"args": [], "kwargs": {"x": values}}
    elif node_name.startswith(electron_dict_prefix):
        values = {}
        for parent in result_obj.transport_graph.get_dependencies(task_id):
            key = result_obj.transport_graph.get_edge_value(parent, task_id, "edge_name")
            value = result_obj._get_node_output(parent)
            values[key] = value
        task_inputs = {"args": [], "kwargs": {"x": values}}
    else:
        task_inputs = {"args": [], "kwargs": {}}

        for parent in result_obj.transport_graph.get_dependencies(task_id):

            param_type = result_obj.transport_graph.get_edge_value(parent, task_id, "param_type")

            value = result_obj._get_node_output(parent)

            if param_type == "arg":
                task_inputs["args"].append(value)

            elif param_type == "kwarg":
                key = result_obj.transport_graph.get_edge_value(parent, task_id, "edge_name")

                task_inputs["kwargs"][key] = value
    return task_inputs


def is_sublattice(task_name: str = None) -> bool:
    """Check if the transport graph task node is a sublattice. When the workflow is first
    dispatched, the build graph step is responsible for attaching a `sublattice` prefix to the
    corresponding task node."""

    return task_name.startswith(sublattice_prefix)


def are_tasks_running(result_obj: Result) -> bool:
    """Check if any of the tasks are still running. A task is considered not `running` if it was completed, failed or cancelled."""

    return any(
        result_obj._get_node_status(task_id) in [Result.RUNNING, Result.NEW_OBJ]
        for task_id in range(result_obj._num_nodes)
        if not result_obj._get_node_name(task_id).startswith(parameter_prefix)
    )


def get_task_order(result_obj: Result) -> List[List]:
    """Find the order in which the tasks need to be executed. At the current moment this is
    based simply on the topologically sorted task nodes in the graph. In the future,
    this function can become much more sophisticated and optimized.
    """

    return result_obj.transport_graph.get_topologically_sorted_graph()


def send_task_list_to_runner(dispatch_id, tasks_list) -> List[int]:

    logger.warning(f"Inside send_task_list_to_runner with dispatch_id {dispatch_id}")
    logger.warning(f"Inside send_task_list_to_runner with tasks_list {tasks_list}")

    # Example tasks_list:
    # tasks_list = [
    #     {
    #         "task_id": 0,
    #         "func": result_object.transport_graph.get_node_value(0, "function"),
    #         "args": [2 + 2],
    #         "kwargs": {},
    #         "executor": result_object.transport_graph.get_node_value(0, "metadata")[
    #             "executor"
    #         ],
    #         "results_dir": result_object.results_dir,
    #     },
    #     {
    #         "task_id": 2,
    #         "func": result_object.transport_graph.get_node_value(2, "function"),
    #         "args": [2, 10],
    #         "kwargs": {},
    #         "executor": result_object.transport_graph.get_node_value(2, "metadata")[
    #             "executor"
    #         ],
    #         "results_dir": result_object.results_dir,
    #     },
    # ]
    # response = requests.post(url=url_endpoint, files={"tasks": pickle.dumps(tasks_list)})

    # Set the url endpoint
    url_endpoint = RunnerURI().get_route(f"workflow/{dispatch_id}/tasks")

    # Send the tasks list as file
    response = requests.post(url=url_endpoint, files={"tasks": BytesIO(pickle.dumps(tasks_list))})

    # Raise error if occurred
    response.raise_for_status()

    return response.json()["left_out_task_ids"]


def send_result_object_to_result_service(result_object: Result):
    """Send result object to the result microservice."""

    url_endpoint = ResultsURI().get_route("workflow/results")

    response = requests.post(
        url=url_endpoint, files={"result_pkl_file": BytesIO(pickle.dumps(result_object))}
    )
    response.raise_for_status()

    return response.text


def send_task_update_to_result_service(dispatch_id: str, task_execution_result: dict):

    url_endpoint = ResultsURI().get_route(f"workflow/results/{dispatch_id}")

    response = requests.put(
        url=url_endpoint, files={"task": BytesIO(pickle.dumps(task_execution_result))}
    )
    response.raise_for_status()

    return response.text


def send_task_update_to_ui(dispatch_id: str, task_id: int):
    """Send task update to UI backend microservice."""

    url_endpoint = UIBackendURI().get_route(f"ui/workflow/{dispatch_id}/task/{task_id}")

    response = requests.put(url=url_endpoint)
    response.raise_for_status()

    return response.text


def get_result_object_from_result_service(dispatch_id: str):
    logger.warning(f"getting result object with id {dispatch_id}")

    url_endpoint = ResultsURI().get_route(f"workflow/results/{dispatch_id}")

    response = requests.get(url=url_endpoint, stream=True)
    response.raise_for_status()

    return pickle.loads(response.content)


def update_result_and_ui(result_obj: Result, task_id: int) -> Dict[str, str]:
    """Write the updated result to the database and update the UI."""

    resp_1 = send_result_object_to_result_service(result_obj)
    resp_2 = send_task_update_to_ui(dispatch_id=result_obj.dispatch_id, task_id=task_id)
    return {"update_result_response": resp_1, "update_ui_response": resp_2}


def send_cancel_task_to_runner(dispatch_id: str, task_id: int) -> Tuple[str, str]:

    url_endpoint = RunnerURI().get_route(f"workflow/{dispatch_id}/task/{task_id}")
    response = requests.delete(url=url_endpoint)
    response.raise_for_status()

    return response.json()["cancelled_dispatch_id"], response.json()["cancelled_task_id"]


def is_sublattice_dispatch_id(dispatch_id: str):
    return ":" in dispatch_id


def send_task_update_to_dispatcher(dispatch_id, task_result):

    url = DispatcherURI().get_route(f"workflow/{dispatch_id}")

    logger.warning(
        f"Sending task result to get updated in dispatcher with task result: {task_result}"
    )
    logger.warning(f"URL: {url}")

    response = requests.put(url=url, files={"task_execution_results": pickle.dumps(task_result)})

    logger.warning("Put done with response")

    response.raise_for_status()


def generate_task_result(
    task_id,
    start_time=None,
    end_time=None,
    status=None,
    output=None,
    error=None,
    stdout=None,
    stderr=None,
    info=None,
):

    return {
        "task_id": task_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "output": output,
        "error": error,
        "stdout": stdout,
        "stderr": stderr,
        "info": info,
    }


def get_parent_id_and_task_id(dispatch_id: str):

    if not is_sublattice_dispatch_id(dispatch_id):
        return False, False

    splits = dispatch_id.split(":")
    parent_dispatch_id, task_id = ":".join(splits[:-1]), splits[-1]
    return parent_dispatch_id, int(task_id)
