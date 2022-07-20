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
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Set, Union

import cloudpickle
import cloudpickle as pickle
import networkx as nx
import yaml
from sqlalchemy import and_, update
from sqlalchemy.orm import Session

from .._data_store import DataStore, DataStoreNotInitializedError, models
from .._shared_files import logger
from .._shared_files.context_managers import active_lattice_manager
from .._shared_files.defaults import prefix_separator, sublattice_prefix
from .._shared_files.util_classes import RESULT_STATUS, Status
from .._workflow.transport import TransportableObject
from .utils import _db_path, convert_to_lattice_function_call
from .write_result_to_db import (
    get_electron_type,
    insert_electron_dependency_data,
    insert_electrons_data,
    insert_lattices_data,
    update_electrons_data,
    update_lattice_completed_electron_num,
    update_lattices_data,
)

if TYPE_CHECKING:
    from .._shared_files.util_classes import Status
    from .._workflow.lattice import Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info

LATTICE_FUNCTION_FILENAME = "function.pkl"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_EXECUTOR_FILENAME = "executor.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.pkl"
LATTICE_RESULTS_FILENAME = "results.pkl"
LATTICE_TRANSPORT_GRAPH_FILENAME = "transport_graph.pkl"
LATTICE_STORAGE_TYPE = "local"

ELECTRON_FUNCTION_FILENAME = "function.pkl"
ELECTRON_FUNCTION_STRING_FILENAME = "function_string.txt"
ELECTRON_KEY_FILENAME = "key.pkl"
ELECTRON_VALUE_FILENAME = "value.pkl"
ELECTRON_EXECUTOR_FILENAME = "executor.pkl"
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

    def __init__(self, lattice: "Lattice", results_dir: str, dispatch_id: str = None) -> None:

        self._start_time = None
        self._end_time = None

        self._results_dir = results_dir

        self._lattice = lattice
        self._dispatch_id = dispatch_id

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

        node_outputs = self.get_all_node_outputs(
            DataStore(db_URL=f"sqlite+pysqlite:///{_db_path()}")
        )
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
            node_name = self.lattice.transport_graph.get_node_value(node_id, "name")

            self.lattice.transport_graph.set_node_value(node_id, "node_name", node_name)

            self.lattice.transport_graph.set_node_value(node_id, "start_time", None)

            self.lattice.transport_graph.set_node_value(node_id, "end_time", None)

            self.lattice.transport_graph.set_node_value(node_id, "status", Result.NEW_OBJ)

            self.lattice.transport_graph.set_node_value(node_id, "output", None)

            self.lattice.transport_graph.set_node_value(node_id, "error", None)

            self.lattice.transport_graph.set_node_value(node_id, "sublattice_result", None)

            self.lattice.transport_graph.set_node_value(node_id, "stdout", None)

            self.lattice.transport_graph.set_node_value(node_id, "stderr", None)

    def get_node_result(self, db: DataStore, node_id: int) -> dict:
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

        # return {
        #     "node_id": node_id,
        #     "node_name": self.lattice.transport_graph.get_node_value(node_id, "node_name"),
        #     "start_time": self.lattice.transport_graph.get_node_value(node_id, "start_time"),
        #     "end_time": self.lattice.transport_graph.get_node_value(node_id, "end_time"),
        #     "status": self.lattice.transport_graph.get_node_value(node_id, "status"),
        #     "output": self.lattice.transport_graph.get_node_value(node_id, "output"),
        #     "error": self.lattice.transport_graph.get_node_value(node_id, "error"),
        #     "sublattice_result": self.lattice.transport_graph.get_node_value(
        #         node_id, "sublattice_result"
        #     ),
        #     "stdout": self.lattice.transport_graph.get_node_value(node_id, "stdout"),
        #     "stderr": self.lattice.transport_graph.get_node_value(node_id, "stderr"),
        # }

        return {
            "node_id": node_id,
            "node_name": self._get_node_name(db, node_id),
            "start_time": self.lattice.transport_graph.get_node_value(node_id, "start_time"),
            "end_time": self.lattice.transport_graph.get_node_value(node_id, "end_time"),
            "status": self._get_node_status(db, node_id),
            "output": self._get_node_output(db, node_id),
            "error": self.lattice.transport_graph.get_node_value(node_id, "error"),
            "sublattice_result": self.lattice.transport_graph.get_node_value(
                node_id, "sublattice_result"
            ),
            "stdout": self.lattice.transport_graph.get_node_value(node_id, "stdout"),
            "stderr": self._get_node_error(db, node_id),
        }

    def get_all_node_outputs(self, db: DataStore) -> dict:
        """
        Return output of every node execution.

        Args:
            None

        Returns:
            node_outputs: A dictionary containing the output of every node execution.
        """
        with Session(db.engine) as session:

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
                    f"{self._get_node_name(db, node_id)}({node_id})"
                ] = self._get_node_output(db, node_id)
            return all_node_outputs

    def get_all_node_results(self, db: DataStore) -> List[Dict]:
        """
        Get all the node results.

        Args:
            None

        Returns:
            node_results: A list of dictionaries containing the result of every node execution.
        """
        with Session(db.engine) as session:

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
                self.get_node_result(db, electron.transport_graph_node_id)
                for electron in electron_records
            ]

    def post_process(self):

        # Copied from server-side _post_process()
        node_outputs = self.get_all_node_outputs(
            DataStore(db_URL=f"sqlite+pysqlite:///{_db_path()}")
        )
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

    def _get_node_name(self, db: DataStore, node_id: int) -> str:
        """
        Returns the name of the node with given node id.

        Args:
            node_id: The node id.

        Returns:
            The name of said node.
        """

        with Session(db.engine) as session:

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

    def _get_node_status(self, db: DataStore, node_id: int) -> "Status":
        """
        Returns the status of a node.

        Args:
            node_id: The node id.

        Returns:
            The status of said node.
        """

        with Session(db.engine) as session:

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

    def _get_node_output(self, db: DataStore, node_id: int) -> Any:
        """
        Return the output of a node.

        Args:
            node_id: The node id.

        Returns:
            output: The output of said node.
                    Will return None if error occured in execution.
        """

        with Session(db.engine) as session:

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
            with open(os.path.join(electron.storage_path, electron.results_filename), "rb") as f:
                return pickle.load(f)

    def _get_node_value(self, db: DataStore, node_id: int) -> Any:
        """
        Return the output of a node.

        Args:
            node_id: The node id.

        Returns:
            output: The output of said node.
                    Will return None if error occured in execution.
        """

        with Session(db.engine) as session:

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
            with open(os.path.join(electron.storage_path, electron.value_filename), "rb") as f:
                return pickle.load(f)

    def _get_node_error(self, db: DataStore, node_id: int) -> Any:
        """
        Return the error of a node.

        Args:
            node_id: The node id.

        Returns:
            error: The error of said node.
                   Will return None if no error occured in execution.
        """

        with Session(db.engine) as session:

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

            with open(os.path.join(electron.storage_path, electron.stderr_filename), "rb") as f:
                return pickle.load(f)

    def _update_node(
        self,
        db: DataStore,
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

        app_log.warning("Inside update node")

        electron_kwargs = {}
        node_path = Path(self.results_dir) / self.dispatch_id / f"node_{node_id}"
        if not node_path.exists():
            node_path.mkdir()

        if node_name is not None:
            self.lattice.transport_graph.set_node_value(node_id, "node_name", node_name)
            electron_kwargs["name"] = node_name

        if start_time is not None:
            self.lattice.transport_graph.set_node_value(node_id, "start_time", start_time)
            electron_kwargs["started_at"] = start_time

        if end_time is not None:
            self.lattice.transport_graph.set_node_value(node_id, "end_time", end_time)
            electron_kwargs["completed_at"] = end_time

        if status is not None:
            self.lattice.transport_graph.set_node_value(node_id, "status", status)
            electron_kwargs["status"] = str(status)

        if output is not None:
            self.lattice.transport_graph.set_node_value(node_id, "output", output)
            with open(node_path / ELECTRON_RESULTS_FILENAME, "wb") as f:
                cloudpickle.dump(output, f)

        if error is not None:
            self.lattice.transport_graph.set_node_value(node_id, "error", error)

        if sublattice_result is not None:
            self.lattice.transport_graph.set_node_value(
                node_id, "sublattice_result", sublattice_result
            )

        if stdout is not None:
            self.lattice.transport_graph.set_node_value(node_id, "stdout", stdout)
            with open(node_path / ELECTRON_STDOUT_FILENAME, "wb") as f:
                cloudpickle.dump(stdout, f)

        if stderr is not None:
            self.lattice.transport_graph.set_node_value(node_id, "stderr", stderr)
            with open(node_path / ELECTRON_STDERR_FILENAME, "wb") as f:
                cloudpickle.dump(stderr, f)

        if str(status) == "COMPLETED":
            update_lattice_completed_electron_num(db, self.dispatch_id)

        with Session(db.engine) as session:
            lattice_id = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .all()[0]
                .id
            )
            session.execute(
                update(models.Electron)
                .where(
                    models.Electron.parent_lattice_id == lattice_id,
                    models.Electron.transport_graph_node_id == node_id,
                )
                .values(updated_at=datetime.now(timezone.utc), **electron_kwargs)
            )
            session.commit()
        app_log.warning("Inside update node - SUCCESS")

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

        app_log.info(f"Directory: {directory}")
        app_log.info(f"Results dir: {self.results_dir}")
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

    def _initialize_results_dir(self):
        """Create the results directory."""

        result_folder_path = os.path.join(self.results_dir, f"{self.dispatch_id}")
        Path(result_folder_path).mkdir(parents=True, exist_ok=True)

    def upsert_lattice_data(self, db: DataStore):
        """Update lattice data"""

        with Session(db.engine) as session:
            lattice_exists = (
                session.query(models.Lattice)
                .where(models.Lattice.dispatch_id == self.dispatch_id)
                .first()
                is not None
            )

        # Store all lattice info that belongs in filenames in the results directory
        data_storage_path = Path(self.results_dir) / self.dispatch_id
        with open(data_storage_path / LATTICE_FUNCTION_FILENAME, "wb") as f:
            cloudpickle.dump(self.lattice.workflow_function, f)

        with open(data_storage_path / LATTICE_FUNCTION_STRING_FILENAME, "wb") as f:
            try:
                cloudpickle.dump(self.lattice.workflow_function_string, f)
            except AttributeError as e:
                app_log.warning(f"{e}")
                cloudpickle.dump(None, f)

        with open(data_storage_path / LATTICE_EXECUTOR_FILENAME, "wb") as f:
            cloudpickle.dump(self.lattice.metadata["executor"], f)

        with open(data_storage_path / LATTICE_ERROR_FILENAME, "wb") as f:
            cloudpickle.dump(self.error, f)

        with open(data_storage_path / LATTICE_INPUTS_FILENAME, "wb") as f:
            cloudpickle.dump(self.inputs, f)

        with open(data_storage_path / LATTICE_RESULTS_FILENAME, "wb") as f:
            cloudpickle.dump(self._result, f)

        with open(data_storage_path / LATTICE_TRANSPORT_GRAPH_FILENAME, "wb") as f:
            cloudpickle.dump(self._lattice.transport_graph, f)

        # Write lattice records to Database
        if not lattice_exists:
            lattice_record_kwarg = {
                "dispatch_id": self.dispatch_id,
                "status": str(self.status),
                "name": self.lattice.__name__,
                "electron_num": self._num_nodes,
                "completed_electron_num": 0,  # None of the nodes have been executed or completed yet.
                "storage_path": str(data_storage_path),
                "storage_type": LATTICE_STORAGE_TYPE,
                "function_filename": LATTICE_FUNCTION_FILENAME,
                "function_string_filename": LATTICE_FUNCTION_STRING_FILENAME,
                "executor_filename": LATTICE_EXECUTOR_FILENAME,
                "error_filename": LATTICE_ERROR_FILENAME,
                "inputs_filename": LATTICE_INPUTS_FILENAME,
                "results_filename": LATTICE_RESULTS_FILENAME,
                "transport_graph_filename": LATTICE_TRANSPORT_GRAPH_FILENAME,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "started_at": self.start_time,
                "completed_at": self.end_time,
            }
            insert_lattices_data(db=db, **lattice_record_kwarg)

        else:
            lattice_record_kwarg = {
                "dispatch_id": self.dispatch_id,
                "status": str(self.status),
                "updated_at": datetime.now(timezone.utc),
                "started_at": self.start_time,
                "completed_at": self.end_time,
            }
            update_lattices_data(db=db, **lattice_record_kwarg)

    def upsert_electron_data(self, db: DataStore):
        """Update electron data"""

        tg = self.lattice.transport_graph
        dirty_nodes = set(tg.dirty_nodes)
        tg.dirty_nodes.clear()  # Ensure that dirty nodes list is reset once the data is updated

        with Session(db.engine) as session:
            for node_id in dirty_nodes:

                node_path = Path(self.results_dir) / self.dispatch_id / f"node_{node_id}"

                if not node_path.exists():
                    node_path.mkdir()

                attribute_name = tg.get_node_value(node_key=node_id, value_key="name")

                try:
                    node_key = tg.get_node_value(node_key=node_id, value_key="key")
                except KeyError:
                    node_key = None

                started_at = tg.get_node_value(node_key=node_id, value_key="start_time")
                completed_at = tg.get_node_value(node_key=node_id, value_key="end_time")

                # Write all electron data to the appropriate filepaths
                with open(node_path / ELECTRON_FUNCTION_FILENAME, "wb") as f:
                    cloudpickle.dump(tg.get_node_value(node_id, "function"), f)

                with open(node_path / ELECTRON_FUNCTION_STRING_FILENAME, "wb") as f:
                    try:
                        function_string = tg.get_node_value(node_id, "function_string")
                    except KeyError:
                        function_string = None
                    cloudpickle.dump(function_string, f)

                with open(node_path / ELECTRON_VALUE_FILENAME, "wb") as f:
                    try:
                        node_value = tg.get_node_value(node_id, "value")
                    except KeyError:
                        node_value = None
                    cloudpickle.dump(node_value, f)

                with open(node_path / ELECTRON_EXECUTOR_FILENAME, "wb") as f:
                    cloudpickle.dump(tg.get_node_value(node_id, "metadata")["executor"], f)

                with open(node_path / ELECTRON_DEPS_FILENAME, "wb") as f:
                    cloudpickle.dump(tg.get_node_value(node_id, "metadata")["deps"], f)

                with open(node_path / ELECTRON_CALL_BEFORE_FILENAME, "wb") as f:
                    cloudpickle.dump(tg.get_node_value(node_id, "metadata")["call_before"], f)

                with open(node_path / ELECTRON_CALL_AFTER_FILENAME, "wb") as f:
                    cloudpickle.dump(tg.get_node_value(node_id, "metadata")["call_after"], f)

                with open(node_path / ELECTRON_STDOUT_FILENAME, "wb") as f:
                    try:
                        node_stdout = tg.get_node_value(node_id, "stdout")
                    except KeyError:
                        node_stdout = None
                    cloudpickle.dump(node_stdout, f)

                with open(node_path / ELECTRON_STDERR_FILENAME, "wb") as f:
                    try:
                        node_stderr = tg.get_node_value(node_id, "stderr")
                    except KeyError:
                        node_stderr = None
                    cloudpickle.dump(node_stderr, f)

                with open(node_path / ELECTRON_INFO_FILENAME, "wb") as f:
                    try:
                        node_info = tg.get_node_value(node_id, "info")
                    except KeyError:
                        node_info = None
                    cloudpickle.dump(node_info, f)

                with open(node_path / ELECTRON_RESULTS_FILENAME, "wb") as f:
                    try:
                        node_output = tg.get_node_value(node_id, "output")
                    except KeyError:
                        node_output = TransportableObject(None)
                    if not isinstance(node_output, TransportableObject):
                        node_output = TransportableObject(node_output)
                    cloudpickle.dump(node_output, f)

                with open(node_path / ELECTRON_KEY_FILENAME, "wb") as f:
                    cloudpickle.dump(node_key, f)

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

                if not electron_exists:
                    electron_record_kwarg = {
                        "parent_dispatch_id": self.dispatch_id,
                        "transport_graph_node_id": node_id,
                        "type": get_electron_type(
                            tg.get_node_value(node_key=node_id, value_key="name")
                        ),
                        "name": tg.get_node_value(node_key=node_id, value_key="name"),
                        "status": str(tg.get_node_value(node_key=node_id, value_key="status")),
                        "storage_type": ELECTRON_STORAGE_TYPE,
                        "storage_path": str(node_path),
                        "function_filename": ELECTRON_FUNCTION_FILENAME,
                        "function_string_filename": ELECTRON_FUNCTION_STRING_FILENAME,
                        "executor_filename": ELECTRON_EXECUTOR_FILENAME,
                        "results_filename": ELECTRON_RESULTS_FILENAME,
                        "value_filename": ELECTRON_VALUE_FILENAME,
                        "attribute_name": attribute_name,
                        "key_filename": ELECTRON_KEY_FILENAME,
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
                    insert_electrons_data(db=db, **electron_record_kwarg)

                else:
                    electron_record_kwarg = {
                        "parent_dispatch_id": self.dispatch_id,
                        "transport_graph_node_id": node_id,
                        "status": str(tg.get_node_value(node_key=node_id, value_key="status")),
                        "started_at": started_at,
                        "updated_at": datetime.now(timezone.utc),
                        "completed_at": completed_at,
                    }
                    update_electrons_data(db=db, **electron_record_kwarg)

    def insert_electron_dependency_data(self, db: DataStore):
        """Update electron dependency data"""

        # Insert electron dependency records if they don't exist
        with Session(db.engine) as session:
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

        if not electron_dependencies_exist:
            insert_electron_dependency_data(
                db=db, dispatch_id=self.dispatch_id, lattice=self.lattice
            )

    def persist(self, db: DataStore) -> None:
        """Save Result object to a DataStoreSession. Changes are queued until
        committed by the caller."""

        self._initialize_results_dir()

        if not db:
            raise DataStoreNotInitializedError

        self.upsert_lattice_data(db)
        self.upsert_electron_data(db)
        self.insert_electron_dependency_data(db)

    def _convert_to_electron_result(self) -> Any:
        """
        Convert the result object to an electron's result.

        Args:
            None

        Returns:
            result: The final output of the dispatch.
        """

        return self._result

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

        dispatch_function = f"# File created by Covalent using version {pkg_resources.get_distribution('covalent').version}\n"
        dispatch_function += f"# Dispatch ID: {self.dispatch_id}\n"
        dispatch_function += f"# Workflow status: {self.status}\n"
        dispatch_function += f"# Workflow start time: {self.start_time}\n"
        dispatch_function += f"# Workflow end time: {self.end_time}" + "\n"

        dispatch_function += "# Covalent result -"
        result_string_lines = str(self.encoded_result.object_string).split("\n")
        if len(result_string_lines) == 1:
            dispatch_function += f" {self.encoded_result.object_string}\n\n"
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
                function = self.lattice.transport_graph.get_node_value(nodes, value_key="function")
                if (
                    function.object_string != "None"
                    and function.attrs["name"] not in functions_added
                ):

                    function_str = self.lattice.transport_graph.get_node_value(
                        nodes, value_key="function_string"
                    )
                    function_str = _filter_cova_decorators(
                        function_str,
                        self.lattice.cova_imports,
                    )
                    dispatch_function += function_str
                    functions_added.append(function.attrs["name"])

        lattice_function_str = convert_to_lattice_function_call(
            self.lattice.workflow_function_string,
            self.lattice.workflow_function.attrs["name"],
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
