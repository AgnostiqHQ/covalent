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
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Set, Union

from sqlalchemy import and_

from .._data_store import models, workflow_db
from .._shared_files import logger
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import prefix_separator, sublattice_prefix
from .._shared_files.util_classes import RESULT_STATUS, Status
from .._workflow.lattice import Lattice
from .._workflow.transport import TransportableObject
from .write_result_to_db import (
    get_electron_type,
    insert_electron_dependency_data,
    insert_electrons_data,
    insert_lattices_data,
    load_file,
    store_file,
    update_electrons_data,
    update_lattice_completed_electron_num,
    update_lattices_data,
)

if TYPE_CHECKING:
    from .._shared_files.util_classes import Status

app_log = logger.app_log
log_stack_info = logger.log_stack_info

LATTICE_FUNCTION_FILENAME = "function.pkl"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_DOCSTRING_FILENAME = "function_docstring.txt"
LATTICE_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.pkl"
LATTICE_NAMED_ARGS_FILENAME = "named_args.pkl"
LATTICE_NAMED_KWARGS_FILENAME = "named_kwargs.pkl"
LATTICE_RESULTS_FILENAME = "results.pkl"
LATTICE_TRANSPORT_GRAPH_FILENAME = "transport_graph.pkl"
LATTICE_DEPS_FILENAME = "deps.pkl"
LATTICE_CALL_BEFORE_FILENAME = "call_before.pkl"
LATTICE_CALL_AFTER_FILENAME = "call_after.pkl"
LATTICE_COVA_IMPORTS_FILENAME = "cova_imports.pkl"
LATTICE_LATTICE_IMPORTS_FILENAME = "lattice_imports.pkl"
LATTICE_STORAGE_TYPE = "local"

ELECTRON_FUNCTION_FILENAME = "function.pkl"
ELECTRON_FUNCTION_STRING_FILENAME = "function_string.txt"
ELECTRON_VALUE_FILENAME = "value.pkl"
ELECTRON_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
ELECTRON_STDOUT_FILENAME = "stdout.log"
ELECTRON_STDERR_FILENAME = "stderr.log"
ELECTRON_INFO_FILENAME = "info.log"
ELECTRON_RESULTS_FILENAME = "results.pkl"
ELECTRON_DEPS_FILENAME = "deps.pkl"
ELECTRON_CALL_BEFORE_FILENAME = "call_before.pkl"
ELECTRON_CALL_AFTER_FILENAME = "call_after.pkl"
ELECTRON_STORAGE_TYPE = "local"


class Result:
    """
    Result class to store and perform operations on the result obtained from a dispatch.

    Attributes:
        lattice: "Lattice" object which was dispatched.
        results_dir: Directory where the result will be stored.
                     It'll be in the format of "<results_dir>/<dispatch_id>/".
        dispatch_id: Dispatch id assigned to this dispatch.
        root_dispatch_id: Dispatch id of the root lattice in a hierarchy of sublattice workflows.
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
    POSTPROCESSING = RESULT_STATUS.POSTPROCESSING
    PENDING_POSTPROCESSING = RESULT_STATUS.PENDING_POSTPROCESSING
    POSTPROCESSING_FAILED = RESULT_STATUS.POSTPROCESSING_FAILED
    RUNNING = RESULT_STATUS.RUNNING
    FAILED = RESULT_STATUS.FAILED
    CANCELLED = RESULT_STATUS.CANCELLED

    def __init__(self, lattice: Lattice, results_dir: str, dispatch_id: str = None) -> None:

        self._start_time = None
        self._end_time = None

        self._results_dir = results_dir

        self._lattice = lattice
        self._dispatch_id = dispatch_id

        self._root_dispatch_id = dispatch_id

        self._status = Result.NEW_OBJ

        self._result = TransportableObject(None)

        self._num_nodes = -1

        self._inputs = {"args": [], "kwargs": {}}
        if lattice.args:
            self._inputs["args"] = lattice.args
        if lattice.kwargs:
            self._inputs["kwargs"] = lattice.kwargs

        self._error = None

    def __str__(self):
        """String representation of the result object"""

        arg_str_repr = [e.object_string for e in self.inputs["args"]]
        kwarg_str_repr = {key: value.object_string for key, value in self.inputs["kwargs"].items()}

        show_result_str = f"""
Lattice Result
==============
status: {self._status}
result: {self.result}
input args: {arg_str_repr}
input kwargs: {kwarg_str_repr}
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
            show_result_str += f"{k}: {v.object_string}\n"

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
    def lattice(self) -> Lattice:
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
    def root_dispatch_id(self) -> str:
        """
        Dispatch id of the root dispatch
        """

        return self._root_dispatch_id

    @property
    def status(self) -> Status:
        """
        Status of current dispatch.
        """

        return self._status

    @property
    def encoded_result(self) -> TransportableObject:
        """
        Encoded final result of current dispatch
        """
        return self._result

    @property
    def result(self) -> Union[int, float, list, dict]:
        """
        Final result of current dispatch.
        """

        return self._result.get_deserialized()

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
            "node_name": self._get_node_name(node_id),
            "start_time": self.lattice.transport_graph.get_node_value(node_id, "start_time"),
            "end_time": self.lattice.transport_graph.get_node_value(node_id, "end_time"),
            "status": self._get_node_status(node_id),
            "output": self._get_node_output(node_id),
            "error": self.lattice.transport_graph.get_node_value(node_id, "error"),
            "sublattice_result": self.lattice.transport_graph.get_node_value(
                node_id, "sublattice_result"
            ),
            "stdout": self.lattice.transport_graph.get_node_value(node_id, "stdout"),
            "stderr": self._get_node_error(node_id),
        }

    def get_all_node_outputs(self) -> dict:
        """
        Return output of every node execution.

        Args:
            None

        Returns:
            node_outputs: A dictionary containing the output of every node execution.
        """
        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                .id
            )
            electron_records = (
                session.query(models.Electron)
                .where(models.Electron.parent_lattice_id == lattice_id)
                .all()
            )
            all_node_outputs = {}
            for electron in electron_records:
                node_id = electron.transport_graph_node_id
                all_node_outputs[
                    f"{self._get_node_name(node_id=node_id)}({node_id})"
                ] = self._get_node_output(node_id=node_id)
            return all_node_outputs

    def get_all_node_results(self) -> List[Dict]:
        """
        Get all the node results.

        Args:
            None

        Returns:
            node_results: A list of dictionaries containing the result of every node execution.
        """
        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                .id
            )
            electron_records = (
                session.query(models.Electron)
                .where(models.Electron.parent_lattice_id == lattice_id)
                .all()
            )
            return [
                self.get_node_result(node_id=electron.transport_graph_node_id)
                for electron in electron_records
            ]

    def post_process(self):

        # Copied from server-side _post_process()
        node_outputs = self.get_all_node_outputs()
        ordered_node_outputs = []
        for i, item in enumerate(node_outputs.items()):
            key, val = item
            if not key.startswith(prefix_separator) or key.startswith(sublattice_prefix):
                ordered_node_outputs.append((i, val))

        lattice = self._lattice

        with active_lattice_manager.claim(lattice):
            lattice.post_processing = True
            lattice.electron_outputs = ordered_node_outputs
            workflow_function = lattice.workflow_function.get_deserialized()
            result = workflow_function(*lattice.args, **lattice.kwargs)
            lattice.post_processing = False
        return result

    def _get_node_name(self, node_id: int) -> str:
        """
        Returns the name of the node with given node id.

        Args:
            node_id: The node id.

        Returns:
            The name of said node.
        """

        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                .id
            )
            return (
                session.query(models.Electron)
                .where(
                    and_(
                        models.Electron.parent_lattice_id == lattice_id,
                        models.Electron.transport_graph_node_id == node_id,
                    )
                )
                .first()
                .name
            )

    def _get_node_status(self, node_id: int) -> "Status":
        """
        Returns the status of a node.

        Args:
            node_id: The node id.

        Returns:
            The status of said node.
        """

        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
            ).id
            return (
                session.query(models.Electron)
                .where(
                    and_(
                        models.Electron.parent_lattice_id == lattice_id,
                        models.Electron.transport_graph_node_id == node_id,
                    )
                )
                .first()
                .status
            )

    def _get_node_output(self, node_id: int) -> Any:
        """
        Return the output of a node.

        Args:
            node_id: The node id.

        Returns:
            output: The output of said node.
                    Will return None if error occured in execution.
        """

        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                .id
            )
            electron = (
                session.query(models.Electron)
                .where(
                    (
                        and_(
                            models.Electron.parent_lattice_id == lattice_id,
                            models.Electron.transport_graph_node_id == node_id,
                        )
                    )
                )
                .first()
            )
            return load_file(
                storage_path=electron.storage_path, filename=electron.results_filename
            )

    def _get_node_value(self, node_id: int) -> Any:
        """
        Return the output of a node.

        Args:
            node_id: The node id.

        Returns:
            output: The output of said node.
                    Will return None if error occured in execution.
        """

        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                .id
            )
            electron = (
                session.query(models.Electron)
                .where(
                    (
                        and_(
                            models.Electron.parent_lattice_id == lattice_id,
                            models.Electron.transport_graph_node_id == node_id,
                        )
                    )
                )
                .first()
            )
            return load_file(storage_path=electron.storage_path, filename=electron.value_filename)

    def _get_node_error(self, node_id: int) -> Any:
        """
        Return the error of a node.

        Args:
            node_id: The node id.

        Returns:
            error: The error of said node.
                   Will return None if no error occured in execution.
        """

        with workflow_db.session() as session:

            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                .id
            )
            electron = (
                session.query(models.Electron)
                .where(
                    (
                        and_(
                            models.Electron.parent_lattice_id == lattice_id,
                            models.Electron.transport_graph_node_id == node_id,
                        )
                    )
                )
                .first()
            )
            return load_file(storage_path=electron.storage_path, filename=electron.stderr_filename)

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

        app_log.debug("Inside update node")

        if node_name is not None:
            self.lattice.transport_graph.set_node_value(node_id, "name", node_name)

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

        self.upsert_electron_data()

        app_log.debug("Inside update node - SUCCESS")

    def _initialize_results_dir(self):
        """Create the results directory."""

        result_folder_path = os.path.join(self.results_dir, f"{self.dispatch_id}")
        Path(result_folder_path).mkdir(parents=True, exist_ok=True)

    def upsert_lattice_data(self, electron_id: int = None):
        """Update lattice data"""

        with workflow_db.session() as session:
            lattice_exists = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                is not None
            )

        try:
            workflow_func_string = self.lattice.workflow_function_string
        except AttributeError:
            workflow_func_string = None

        # Store all lattice info that belongs in filenames in the results directory
        data_storage_path = Path(self.results_dir) / self.dispatch_id
        for filename, data in [
            (LATTICE_FUNCTION_FILENAME, self.lattice.workflow_function),
            (LATTICE_FUNCTION_STRING_FILENAME, workflow_func_string),
            (LATTICE_DOCSTRING_FILENAME, self.lattice.__doc__),
            (LATTICE_EXECUTOR_DATA_FILENAME, self.lattice.metadata["executor_data"]),
            (
                LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME,
                self.lattice.metadata["workflow_executor_data"],
            ),
            (LATTICE_ERROR_FILENAME, self.error),
            (LATTICE_INPUTS_FILENAME, self.inputs),
            (LATTICE_NAMED_ARGS_FILENAME, self.lattice.named_args),
            (LATTICE_NAMED_KWARGS_FILENAME, self.lattice.named_kwargs),
            (LATTICE_RESULTS_FILENAME, self._result),
            (LATTICE_TRANSPORT_GRAPH_FILENAME, self._lattice.transport_graph),
            (LATTICE_DEPS_FILENAME, self.lattice.metadata["deps"]),
            (LATTICE_CALL_BEFORE_FILENAME, self.lattice.metadata["call_before"]),
            (LATTICE_CALL_AFTER_FILENAME, self.lattice.metadata["call_after"]),
            (LATTICE_COVA_IMPORTS_FILENAME, self.lattice.cova_imports),
            (LATTICE_LATTICE_IMPORTS_FILENAME, self.lattice.lattice_imports),
        ]:

            store_file(data_storage_path, filename, data)

        # Write lattice records to Database
        if not lattice_exists:
            lattice_record_kwarg = {
                "dispatch_id": self.dispatch_id,
                "electron_id": electron_id,
                "status": str(self.status),
                "name": self.lattice.__name__,
                "docstring_filename": LATTICE_DOCSTRING_FILENAME,
                "electron_num": self._num_nodes,
                "completed_electron_num": 0,  # None of the nodes have been executed or completed yet.
                "storage_path": str(data_storage_path),
                "storage_type": LATTICE_STORAGE_TYPE,
                "function_filename": LATTICE_FUNCTION_FILENAME,
                "function_string_filename": LATTICE_FUNCTION_STRING_FILENAME,
                "executor": self.lattice.metadata["executor"],
                "executor_data_filename": LATTICE_EXECUTOR_DATA_FILENAME,
                "workflow_executor": self.lattice.metadata["workflow_executor"],
                "workflow_executor_data_filename": LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME,
                "error_filename": LATTICE_ERROR_FILENAME,
                "inputs_filename": LATTICE_INPUTS_FILENAME,
                "named_args_filename": LATTICE_NAMED_ARGS_FILENAME,
                "named_kwargs_filename": LATTICE_NAMED_KWARGS_FILENAME,
                "results_filename": LATTICE_RESULTS_FILENAME,
                "transport_graph_filename": LATTICE_TRANSPORT_GRAPH_FILENAME,
                "deps_filename": LATTICE_DEPS_FILENAME,
                "call_before_filename": LATTICE_CALL_BEFORE_FILENAME,
                "call_after_filename": LATTICE_CALL_AFTER_FILENAME,
                "cova_imports_filename": LATTICE_COVA_IMPORTS_FILENAME,
                "lattice_imports_filename": LATTICE_LATTICE_IMPORTS_FILENAME,
                "results_dir": self.results_dir,
                "root_dispatch_id": self.root_dispatch_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "started_at": self.start_time,
                "completed_at": self.end_time,
            }
            insert_lattices_data(**lattice_record_kwarg)

        else:
            lattice_record_kwarg = {
                "dispatch_id": self.dispatch_id,
                "status": str(self.status),
                "electron_num": self._num_nodes,
                "updated_at": datetime.now(timezone.utc),
                "started_at": self.start_time,
                "completed_at": self.end_time,
            }
            update_lattices_data(**lattice_record_kwarg)

    def upsert_electron_data(self):
        """Update electron data"""
        tg = self.lattice.transport_graph
        dirty_nodes = set(tg.dirty_nodes)
        tg.dirty_nodes.clear()  # Ensure that dirty nodes list is reset once the data is updated
        app_log.debug("upsert_electron_data session begin")
        with workflow_db.session() as session:
            app_log.debug("upsert_electron_data session success")
            for node_id in dirty_nodes:

                node_path = Path(self.results_dir) / self.dispatch_id / f"node_{node_id}"

                if not node_path.exists():
                    node_path.mkdir()

                node_name = tg.get_node_value(node_key=node_id, value_key="name")

                try:
                    function_string = tg.get_node_value(node_id, "function_string")
                except KeyError:
                    function_string = None
                try:
                    node_value = tg.get_node_value(node_id, "value")
                except KeyError:
                    node_value = None
                try:
                    node_stdout = tg.get_node_value(node_id, "stdout")
                except KeyError:
                    node_stdout = None
                try:
                    node_stderr = tg.get_node_value(node_id, "stderr")
                except KeyError:
                    node_stderr = None
                try:
                    node_info = tg.get_node_value(node_id, "info")
                except KeyError:
                    node_info = None
                try:
                    node_output = tg.get_node_value(node_id, "output")
                except KeyError:
                    node_output = None

                executor = tg.get_node_value(node_id, "metadata")["executor"]
                started_at = tg.get_node_value(node_key=node_id, value_key="start_time")
                completed_at = tg.get_node_value(node_key=node_id, value_key="end_time")

                for filename, data in [
                    (ELECTRON_FUNCTION_FILENAME, tg.get_node_value(node_id, "function")),
                    (ELECTRON_FUNCTION_STRING_FILENAME, function_string),
                    (ELECTRON_VALUE_FILENAME, node_value),
                    (
                        ELECTRON_EXECUTOR_DATA_FILENAME,
                        tg.get_node_value(node_id, "metadata")["executor_data"],
                    ),
                    (ELECTRON_DEPS_FILENAME, tg.get_node_value(node_id, "metadata")["deps"]),
                    (
                        ELECTRON_CALL_BEFORE_FILENAME,
                        tg.get_node_value(node_id, "metadata")["call_before"],
                    ),
                    (
                        ELECTRON_CALL_AFTER_FILENAME,
                        tg.get_node_value(node_id, "metadata")["call_after"],
                    ),
                    (ELECTRON_STDOUT_FILENAME, node_stdout),
                    (ELECTRON_STDERR_FILENAME, node_stderr),
                    (ELECTRON_INFO_FILENAME, node_info),
                    (ELECTRON_RESULTS_FILENAME, node_output),
                ]:
                    store_file(node_path, filename, data)

                electron_exists = (
                    session.query(models.Electron, models.Lattice)
                    .where(
                        models.Electron.parent_lattice_id == models.Lattice.id,
                        models.Lattice.dispatch_id == self.dispatch_id,
                        models.Electron.transport_graph_node_id == node_id,
                    )
                    .first()
                    is not None
                )

                status = tg.get_node_value(node_key=node_id, value_key="status")
                if not electron_exists:
                    electron_record_kwarg = {
                        "parent_dispatch_id": self.dispatch_id,
                        "transport_graph_node_id": node_id,
                        "type": get_electron_type(
                            tg.get_node_value(node_key=node_id, value_key="name")
                        ),
                        "name": node_name,
                        "status": str(status),
                        "storage_type": ELECTRON_STORAGE_TYPE,
                        "storage_path": str(node_path),
                        "function_filename": ELECTRON_FUNCTION_FILENAME,
                        "function_string_filename": ELECTRON_FUNCTION_STRING_FILENAME,
                        "executor": executor,
                        "executor_data_filename": ELECTRON_EXECUTOR_DATA_FILENAME,
                        "results_filename": ELECTRON_RESULTS_FILENAME,
                        "value_filename": ELECTRON_VALUE_FILENAME,
                        "stdout_filename": ELECTRON_STDOUT_FILENAME,
                        "stderr_filename": ELECTRON_STDERR_FILENAME,
                        "info_filename": ELECTRON_INFO_FILENAME,
                        "deps_filename": ELECTRON_DEPS_FILENAME,
                        "call_before_filename": ELECTRON_CALL_BEFORE_FILENAME,
                        "call_after_filename": ELECTRON_CALL_AFTER_FILENAME,
                        "created_at": datetime.now(timezone.utc),
                        "updated_at": datetime.now(timezone.utc),
                        "started_at": started_at,
                        "completed_at": completed_at,
                    }
                    insert_electrons_data(**electron_record_kwarg)

                else:
                    electron_record_kwarg = {
                        "parent_dispatch_id": self.dispatch_id,
                        "transport_graph_node_id": node_id,
                        "name": node_name,
                        "status": str(status),
                        "started_at": started_at,
                        "updated_at": datetime.now(timezone.utc),
                        "completed_at": completed_at,
                    }
                    update_electrons_data(**electron_record_kwarg)
                    if status == Result.COMPLETED:
                        update_lattice_completed_electron_num(self.dispatch_id)

    def insert_electron_dependency_data(self):
        """Update electron dependency data"""

        # Insert electron dependency records if they don't exist
        with workflow_db.session() as session:
            electron_dependencies_exist = (
                session.query(models.ElectronDependency, models.Electron, models.Lattice)
                .where(
                    models.Electron.id == models.ElectronDependency.electron_id,
                    models.Electron.parent_lattice_id == models.Lattice.id,
                    models.Lattice.dispatch_id == self.dispatch_id,
                )
                .first()
                is not None
            )
        app_log.debug("electron_dependencies_exist is " + str(electron_dependencies_exist))
        if not electron_dependencies_exist:
            insert_electron_dependency_data(dispatch_id=self.dispatch_id, lattice=self.lattice)

    def persist(self, electron_id: int = None) -> None:
        """Save Result object to a DataStoreSession. Changes are queued until
        committed by the caller.

        Args:
            electron_id: (hack) DB-generated id for the parent electron
                if the workflow is actually a subworkflow
        """

        self._initialize_results_dir()
        app_log.debug("upsert start")
        self.upsert_lattice_data(electron_id=electron_id)
        self.upsert_electron_data()
        app_log.debug("upsert complete")
        self.insert_electron_dependency_data()
        app_log.debug("persist complete")

    def _convert_to_electron_result(self) -> Any:
        """
        Convert the result object to an electron's result.

        Args:
            None

        Returns:
            result: The final output of the dispatch.
        """

        return self._result


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


def get_unique_id() -> str:
    """
    Get a unique ID.

    Args:
        None

    Returns:
        str: Unique ID
    """

    return str(uuid.uuid4())


def initialize_result_object(
    json_lattice: str, parent_result_object: Result = None, parent_electron_id: int = None
) -> Result:
    """Convenience function for constructing a result object from a json-serialized lattice.

    Args:
        json_lattice: a JSON-serialized lattice
        parent_result_object: the parent result object if json_lattice is a sublattice
        parent_electron_id: the DB id of the parent electron (for sublattices)

    Returns:
        Result: result object
    """

    dispatch_id = get_unique_id()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"], dispatch_id)
    if parent_result_object:
        result_object._root_dispatch_id = parent_result_object._root_dispatch_id

    result_object._initialize_nodes()
    app_log.debug("2: Constructed result object and initialized nodes.")

    result_object.persist(electron_id=parent_electron_id)
    app_log.debug("Result object persisted.")

    return result_object
