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

"""Result object."""

import os
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Set, Union

import cloudpickle as pickle
import yaml

from .._shared_files import logger
from .._shared_files.util_classes import RESULT_STATUS, Status
from .utils import convert_to_lattice_function_call

if TYPE_CHECKING:
    from .._shared_files.util_classes import Status
    from .._workflow.lattice import Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class Result:
    """
    Result class to store and perform operations on the result obtained from a dispatch.

    Attributes:
        lattice: "Lattice" object which was dispatched.
        results_dir: Directory where the result will be stored.
                     It'll be in the format of "<results_dir>/<dispatch_id>/".
        dispatch_id: Dispatch id assigned to this dispatch.
        status: Status of the result. It'll be one of the following:
                - Result.NEW_OBJ: When it is a new result object.
                - Result.COMPLETED: When processing of all the nodes has completed successfully.
                - Result.RUNNING: When some node executions are in process.
                - Result.FAILED: When one or more node executions have failed.
                - Result.CANCELLED: When the dispatch was cancelled.
        result: Final result of the dispatch, i.e whatever the "Lattice" was returning as a function.
        inputs: Inputs sent to the "Lattice" function for dispatching.
        error: Error due to which the execution failed.

    Functions:
        save_result: Save the result object to the passed results directory or to self.results_dir by default.
        get_all_node_outputs: Return all the outputs of all the node executions.
    """

    NEW_OBJ = RESULT_STATUS.NEW_OBJECT
    COMPLETED = RESULT_STATUS.COMPLETED
    RUNNING = RESULT_STATUS.RUNNING
    FAILED = RESULT_STATUS.FAILED
    CANCELLED = RESULT_STATUS.CANCELLED

    def __init__(self, lattice: "Lattice", results_dir: str, dispatch_id: str = None) -> None:

        self._start_time = None
        self._end_time = None

        self._results_dir = results_dir

        self._lattice = lattice
        self._dispatch_id = dispatch_id

        self._status = Result.NEW_OBJ

        self._result = None

        self._inputs = {"args": [], "kwargs": {}}
        if lattice.args:
            self._inputs["args"] = lattice.args
        if lattice.kwargs:
            self._inputs["kwargs"] = lattice.kwargs

        self._error = None

    def __str__(self):
        show_result_str = f"""
Lattice Result
==============
status: {self._status}
result: {self.result}
inputs: {self.inputs}
error: {self.error}

start_time: {self.start_time}
end_time: {self.end_time}

results_dir: {self.results_dir}
dispatch_id: {self.dispatch_id}

Node Outputs
------------
"""

        node_outputs = self.get_all_node_outputs()
        for k, v in node_outputs.items():
            show_result_str += f"{k}: {v}\n"

        return show_result_str

    @property
    def start_time(self) -> datetime:
        """
        Start time of processing the dispatch.
        """

        return self._start_time

    @property
    def end_time(self) -> datetime:
        """
        End time of processing the dispatch.
        """

        return self._end_time

    @property
    def results_dir(self) -> str:
        """
        Results directory used to save this result object.
        """

        return self._results_dir

    @property
    def lattice(self) -> "Lattice":
        """
        "Lattice" object which was dispatched.
        """

        return self._lattice

    @property
    def dispatch_id(self) -> str:
        """
        Dispatch id of current dispatch.
        """

        return self._dispatch_id

    @property
    def status(self) -> Status:
        """
        Status of current dispatch.
        """

        return self._status

    @property
    def result(self) -> Union[int, float, list, dict]:
        """
        Final result of current dispatch.
        """

        return self._result

    @property
    def inputs(self) -> dict:
        """
        Inputs sent to the "Lattice" function for dispatching.
        """

        return self._inputs

    @property
    def error(self) -> str:
        """
        Error due to which the dispatch failed.
        """

        return self._error

    def _initialize_nodes(self) -> None:
        """
        Initialize the nodes of the transport graph with a blank result.
        This is called after `self.lattice.transport_graph` has been deserialized.

        Args:
            None

        Returns:
            None
        """

        self._num_nodes = self.lattice.transport_graph.get_internal_graph_copy().number_of_nodes()
        for node_id in range(self._num_nodes):
            node_name = (
                self.lattice.transport_graph.get_node_value(node_id, "name") + f"({node_id})"
            )

            self.lattice.transport_graph.set_node_value(node_id, "node_name", node_name)

            self.lattice.transport_graph.set_node_value(node_id, "start_time", None)

            self.lattice.transport_graph.set_node_value(node_id, "end_time", None)

            self.lattice.transport_graph.set_node_value(node_id, "status", Result.NEW_OBJ)

            self.lattice.transport_graph.set_node_value(node_id, "output", None)

            self.lattice.transport_graph.set_node_value(node_id, "error", None)

            self.lattice.transport_graph.set_node_value(node_id, "sublattice_result", None)

            self.lattice.transport_graph.set_node_value(node_id, "stdout", None)

            self.lattice.transport_graph.set_node_value(node_id, "stderr", None)

    def get_node_result(self, node_id: int) -> dict:
        """Return the result of a particular node.

        Args:
            node_id: The node id.

        Returns:
            node_result: The result of the node containing below in a dictionary format:
                            - node_id: The node id.
                            - node_name: The name of the node.
                            - start_time: The start time of the node execution.
                            - end_time: The end time of the node execution.
                            - status: The status of the node execution.
                            - output: The output of the node unless error occured in which case None.
                            - error: The error of the node if occured else None.
                            - sublattice_result: The result of the sublattice if any.
                            - stdout: The stdout of the node execution.
                            - stderr: The stderr of the node execution.
        """

        return {
            "node_id": node_id,
            "node_name": self.lattice.transport_graph.get_node_value(node_id, "node_name"),
            "start_time": self.lattice.transport_graph.get_node_value(node_id, "start_time"),
            "end_time": self.lattice.transport_graph.get_node_value(node_id, "end_time"),
            "status": self.lattice.transport_graph.get_node_value(node_id, "status"),
            "output": self.lattice.transport_graph.get_node_value(node_id, "output"),
            "error": self.lattice.transport_graph.get_node_value(node_id, "error"),
            "sublattice_result": self.lattice.transport_graph.get_node_value(
                node_id, "sublattice_result"
            ),
            "stdout": self.lattice.transport_graph.get_node_value(node_id, "stdout"),
            "stderr": self.lattice.transport_graph.get_node_value(node_id, "stderr"),
        }

    def get_all_node_outputs(self) -> dict:
        """
        Return output of every node execution.

        Args:
            None

        Returns:
            node_outputs: A dictionary containing the output of every node execution.
        """

        return {
            self._get_node_name(node_id): self._get_node_output(node_id)
            for node_id in range(self._num_nodes)
        }

    def get_all_node_results(self) -> List[Dict]:
        """
        Get all the node results.

        Args:
            None

        Returns:
            node_results: A list of dictionaries containing the result of every node execution.
        """

        return [self.get_node_result(i) for i in range(self._num_nodes)]

    def _get_node_name(self, node_id: int) -> str:
        """
        Returns the name of the node with given node id.

        Args:
            node_id: The node id.

        Returns:
            node_name: The name of said node.
        """

        return self.lattice.transport_graph.get_node_value(node_id, "node_name")

    def _get_node_status(self, node_id: int) -> "Status":
        """
        Returns the status of a node.

        Args:
            node_id: The node id.

        Returns:
            status: The status of said node.
        """

        return self.lattice.transport_graph.get_node_value(node_id, "status")

    def _get_node_output(self, node_id: int) -> Any:
        """
        Return the output of a node.

        Args:
            node_id: The node id.

        Returns:
            output: The output of said node.
                    Will return None if error occured in execution.
        """

        return self.lattice.transport_graph.get_node_value(node_id, "output")

    def _get_node_error(self, node_id: int) -> Any:
        """
        Return the error of a node.

        Args:
            node_id: The node id.

        Returns:
            error: The error of said node.
                   Will return None if no error occured in execution.
        """

        return self.lattice.transport_graph.get_node_value(node_id, "error")

    def _update_node(
        self,
        node_id: int,
        node_name: str = None,
        start_time: "datetime" = None,
        end_time: "datetime" = None,
        status: "Status" = None,
        output: Any = None,
        error: Exception = None,
        sublattice_result: "Result" = None,
        stdout: str = None,
        stderr: str = None,
    ) -> None:
        """
        Update the node result in the transport graph.
        Called after any change in node's execution state.

        Args:
            node_id: The node id.
            node_name: The name of the node.
            start_time: The start time of the node execution.
            end_time: The end time of the node execution.
            status: The status of the node execution.
            output: The output of the node unless error occured in which case None.
            error: The error of the node if occured else None.
            sublattice_result: The result of the sublattice if any.
            stdout: The stdout of the node execution.
            stderr: The stderr of the node execution.

        Returns:
            None
        """

        if node_name is not None:
            self.lattice.transport_graph.set_node_value(node_id, "node_name", node_name)

        if start_time is not None:
            self.lattice.transport_graph.set_node_value(node_id, "start_time", start_time)

        if end_time is not None:
            self.lattice.transport_graph.set_node_value(node_id, "end_time", end_time)

        if status is not None:
            self.lattice.transport_graph.set_node_value(node_id, "status", status)

        if output is not None:
            self.lattice.transport_graph.set_node_value(node_id, "output", output)

        if error is not None:
            self.lattice.transport_graph.set_node_value(node_id, "error", error)

        if sublattice_result is not None:
            self.lattice.transport_graph.set_node_value(
                node_id, "sublattice_result", sublattice_result
            )

        if stdout is not None:
            self.lattice.transport_graph.set_node_value(node_id, "stdout", stdout)

        if stderr is not None:
            self.lattice.transport_graph.set_node_value(node_id, "stderr", stderr)

    def save(self, directory: str = None, write_source: bool = False) -> None:
        """
        Save the result object to a file.

        Args:
            directory: The directory to save the result object to.
                       If not specified, the result object will be saved to the
                       `self.results_dir` directory.

        Returns:
            None
        """

        directory = directory or self.results_dir

        result_folder_path = os.path.join(directory, f"{self.dispatch_id}")
        Path(result_folder_path).mkdir(parents=True, exist_ok=True)

        result_info = {
            "dispatch_id": self.dispatch_id,
            "result_status": self.status,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M")
            if self.start_time
            else self.start_time,
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M")
            if self.end_time
            else self.end_time,
        }

        with open(os.path.join(result_folder_path, "result.pkl"), "wb") as f:
            f.write(pickle.dumps(self))

        with open(os.path.join(result_folder_path, "result_info.yaml"), "w") as f:
            yaml.dump(result_info, f)

        if write_source:
            self._write_dispatch_to_python_file()

    def _convert_to_electron_result(self) -> Any:
        """
        Convert the result object to an electron's result.

        Args:
            None

        Returns:
            result: The final output of the dispatch.
        """

        return self.result

    def _write_dispatch_to_python_file(self, directory: str = None) -> None:
        """
        Writes the source code of user function definitions to a python file.

        Args:
            directory: The directory to write the source file to.

        Returns:
            None
        """

        directory = directory or self.results_dir

        import pkg_resources

        dispatch_function = f"# File created by Covalent using version {pkg_resources.get_distribution('cova').version}\n"
        dispatch_function += f"# Dispatch ID: {self.dispatch_id}\n"
        dispatch_function += f"# Workflow status: {self.status}\n"
        dispatch_function += f"# Workflow start time: {self.start_time}\n"
        dispatch_function += f"# Workflow end time: {self.end_time}" + "\n"

        dispatch_function += "# Covalent result -"
        result_string_lines = str(self.result).split("\n")
        if len(result_string_lines) == 1:
            dispatch_function += f" {self.result}\n\n"
        else:
            dispatch_function += "\n"
            for line in result_string_lines:
                dispatch_function += f"# {line}\n"
            dispatch_function += "\n"

        # add imports
        dispatch_function += self.lattice.lattice_imports + "\n" * 2

        directory = directory or self.results_dir
        result_folder_path = os.path.join(directory, f"{self.dispatch_id}")
        Path(result_folder_path).mkdir(parents=True, exist_ok=True)

        # Accumulate the tasks and workflow in a string
        topo_sorted_graph = self.lattice.transport_graph.get_topologically_sorted_graph()
        functions_added = []
        for level in topo_sorted_graph:
            for nodes in level:
                function = self.lattice.transport_graph.get_node_value(
                    nodes, value_key="function"
                ).get_deserialized()
                if function is not None and function.__name__ not in functions_added:

                    function_str = self.lattice.transport_graph.get_node_value(
                        nodes, value_key="function_string"
                    )
                    function_str = _filter_cova_decorators(
                        function_str,
                        self.lattice.cova_imports,
                    )
                    dispatch_function += function_str
                    functions_added.append(function.__name__)

        lattice_function_str = convert_to_lattice_function_call(
            self.lattice.workflow_function_string,
            self.lattice.workflow_function.__name__,
            self.inputs,
        )
        lattice_function_str = _filter_cova_decorators(
            lattice_function_str,
            self.lattice.cova_imports,
        )
        dispatch_function += lattice_function_str

        with open(os.path.join(result_folder_path, "dispatch_source.py"), "w") as f:
            f.write(dispatch_function)


def _filter_cova_decorators(function_string: str, cova_imports: Set[str]) -> str:
    """
    Given a string representing a function, comment out any Covalent-related decorators.

    Args
        function_string: A string representation of a workflow function.

    Returns:
        The function string with Covalent-related decorators commented out.
    """

    has_cova_decorator = False
    in_decorator = 0
    function_lines = function_string.split("\n")
    for i in range(len(function_lines)):
        line = function_lines[i].strip()
        if in_decorator > 0:
            function_lines[i] = f"# {function_lines[i]}"
            in_decorator += line.count("(")
            in_decorator -= line.count(")")
        elif line.startswith("@"):
            decorator_name = line.split("@")[1].split(".")[0].split("(")[0]
            if decorator_name in cova_imports:
                function_lines[i] = f"# {function_lines[i]}"
                has_cova_decorator = True
                in_decorator += line.count("(")
                in_decorator -= line.count(")")

    return "\n".join(function_lines) if has_cova_decorator else function_string
