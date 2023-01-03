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

"""DB-backed lattice"""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.util_classes import RESULT_STATUS, Status

from .._db import models
from .._db.datastore import workflow_db
from .asset import Asset
from .base import DispatchedObject
from .db_interfaces.result_utils import (
    ASSET_KEYS,
    METADATA_KEYS,
    _asset_record_map,
    _meta_record_map,
    _to_asset_meta,
    _to_db_meta,
    _to_pure_meta,
)
from .lattice import Lattice

app_log = logger.app_log


class Result(DispatchedObject):
    def __init__(self, record: models.Lattice, bare: bool = False):
        pure_metadata = _to_pure_meta(record)
        asset_metadata = _to_asset_meta(record)
        db_metadata = _to_db_meta(record)

        self._pure_metadata = pure_metadata
        self._db_metadata = db_metadata
        self._assets = {}

        self._lattice_id = db_metadata["lattice_id"]
        self._electron_id = db_metadata["electron_id"]
        self._storage_path = db_metadata["storage_path"]
        self._storage_type = db_metadata["storage_type"]

        for name in asset_metadata:
            self._assets[name] = Asset(self._storage_path, asset_metadata[name])

        self.lattice = Lattice(record, bare)

        self._task_failed = False
        self._task_cancelled = False

        # For lattice updates
        self._start_time = None
        self._end_time = None
        self._status = None
        self._error = None
        self._result = None

    @property
    def pure_metadata(self):
        return self._pure_metadata

    @pure_metadata.setter
    def pure_metadata(self, meta: Dict):
        self._pure_metadata = meta

    @property
    def db_metadata(self):
        return self._db_metadata

    @db_metadata.setter
    def db_metadata(self, meta: Dict):
        self._db_metadata = meta

    @property
    def assets(self):
        return self._assets

    def _get_db_record(self, session: Session) -> models.Lattice:
        record = session.query(models.Lattice).where(models.Lattice.id == self._lattice_id).first()
        return record

    def meta_record_map(self, key: str) -> str:
        return _meta_record_map[key]

    def _to_pure_meta(self, record):
        return _to_pure_meta(record)

    def _to_db_meta(self, record):
        return _to_db_meta(record)

    @property
    def start_time(self):
        return self.get_pure_metadata("start_time")

    @property
    def end_time(self):
        return self.get_pure_metadata("end_time")

    @property
    def dispatch_id(self):
        return self.get_pure_metadata("dispatch_id")

    @property
    def root_dispatch_id(self):
        return self.get_pure_metadata("root_dispatch_id")

    @property
    def status(self) -> Status:
        return Status(self.get_pure_metadata("status"))

    @property
    def result(self):
        return self.get_asset("result").load_data()

    @property
    def error(self):
        return self.get_asset("error").load_data()

    @property
    def results_dir(self):
        return self.get_pure_metadata("results_dir")

    def commit(self):
        with workflow_db.session() as session:
            if self._start_time is not None:
                self.set_value("start_time", self._start_time, session)
                self._start_time = None

            if self._end_time is not None:
                self.set_value("end_time", self._end_time, session)
                self._end_time = None

            if self._status is not None:
                self.set_value("status", str(self._status), session)
                self._status = None

            if self._error is not None:
                self.set_value("error", self._error, session)
                self._error = None

            if self._result is not None:
                self.set_value("result", self._result, session)
                self._result = None

    def _update_node(
        self,
        node_id: int,
        node_name: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        status: "Status" = None,
        output: Any = None,
        error: Exception = None,
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
            stdout: The stdout of the node execution.
            stderr: The stderr of the node execution.

        Returns:
            None
        """

        app_log.debug("Inside update node")

        with workflow_db.session() as session:
            if node_name is not None:
                self.lattice.transport_graph.set_node_value(node_id, "name", node_name, session)

            if start_time is not None:
                self.lattice.transport_graph.set_node_value(
                    node_id, "start_time", start_time, session
                )

            if end_time is not None:
                self.lattice.transport_graph.set_node_value(node_id, "end_time", end_time, session)

            if status is not None:
                self.lattice.transport_graph.set_node_value(node_id, "status", status, session)
                if status == RESULT_STATUS.COMPLETED:
                    completed_num = self.get_value("completed_electron_num", session)
                    self.set_value("completed_electron_num", completed_num + 1, session)

            if output is not None:
                self.lattice.transport_graph.set_node_value(node_id, "output", output, session)

            if error is not None:
                self.lattice.transport_graph.set_node_value(node_id, "error", error, session)

            if stdout is not None:
                self.lattice.transport_graph.set_node_value(node_id, "stdout", stdout, session)

            if stderr is not None:
                self.lattice.transport_graph.set_node_value(node_id, "stderr", stderr, session)

    def _get_failed_nodes(self) -> List[int]:
        """
        Get the node_id of each failed task
        """
        nodes = []
        num_nodes = self.pure_metadata["num_nodes"]
        tg = self.lattice.transport_graph

        with workflow_db.session() as session:
            return [
                (i, tg.get_node_value(i, "name", session))
                for i in range(num_nodes)
                if tg.get_node_value(i, "status", session) == RESULT_STATUS.FAILED
            ]

    def get_all_node_outputs(self) -> dict:
        """
        Return output of every node execution.

        Args:
            None

        Returns:
            node_outputs: A dictionary containing the output of every node execution.
        """

        all_node_outputs = {}
        tg = self.lattice.transport_graph
        for node_id in tg._graph.nodes:
            node_name = tg.get_node_value(node_id, "name")
            node_output = tg.get_node_value(node_id, "output")
            all_node_outputs[f"{node_name}({node_id})"] = node_output
        return all_node_outputs


def get_result_object(dispatch_id: str, bare: bool = False) -> Result:
    with workflow_db.session() as session:
        record = (
            session.query(models.Lattice).where(models.Lattice.dispatch_id == dispatch_id).first()
        )
        if not record:
            raise RuntimeError(f"Dispatch {dispatch_id} not found")
        return Result(record, bare)
