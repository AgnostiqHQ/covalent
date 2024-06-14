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

"""DB-backed lattice"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from covalent._shared_files import logger
from covalent._shared_files.defaults import postprocess_prefix
from covalent._shared_files.util_classes import RESULT_STATUS, Status

from .._db import models
from .asset import Asset, copy_asset, copy_asset_meta
from .base import DispatchedObject
from .controller import Record
from .db_interfaces.result_utils import ASSET_KEYS  # nopycln: import
from .db_interfaces.result_utils import METADATA_KEYS  # nopycln: import
from .db_interfaces.result_utils import _meta_record_map, get_filters, set_filters
from .electron import ELECTRON_KEYS, Electron
from .lattice import LATTICE_KEYS, Lattice

app_log = logger.app_log

RESULT_KEYS = list(_meta_record_map.keys())


class ResultMeta(Record[models.Lattice]):
    model = models.Lattice

    @classmethod
    def get_toplevel_dispatches(
        cls,
        session: Session,
        *,
        fields: list,
        equality_filters: dict,
        membership_filters: dict,
        for_update: bool = False,
        sort_fields: List[str] = [],
        reverse: bool = True,
        offset: int = 0,
        max_items: int = 10,
    ):
        if len(fields) > 0:
            entities = [getattr(cls.model, attr) for attr in fields]
            stmt = select(*entities)
        else:
            stmt = select(cls.model)

        stmt = stmt.where(models.Lattice.root_dispatch_id == models.Lattice.dispatch_id)

        return cls.get(
            session=session,
            stmt=stmt,
            fields=fields,
            equality_filters=equality_filters,
            membership_filters=membership_filters,
            for_update=for_update,
            sort_fields=sort_fields,
            reverse=reverse,
            offset=offset,
            max_items=max_items,
        )


class ResultAsset(Record[models.LatticeAsset]):
    model = models.LatticeAsset


class Result(DispatchedObject[ResultMeta, ResultAsset]):
    meta_type = ResultMeta
    asset_link_type = ResultAsset
    metadata_keys = RESULT_KEYS

    def __init__(
        self,
        session: Session,
        record: models.Lattice,
        bare: bool = False,
        *,
        keys: list = RESULT_KEYS,
        lattice_keys: list = LATTICE_KEYS,
        electron_keys: list = ELECTRON_KEYS,
    ):
        self._id = record.id
        self._keys = keys
        fields = set(map(Result.meta_record_map, keys))
        self._metadata = ResultMeta(session, record, fields=fields)
        self._assets = {}

        self._lattice_id = record.id
        self._electron_id = record.electron_id

        self.lattice = Lattice(
            session, record, bare, keys=lattice_keys, electron_keys=electron_keys
        )

        self._task_failed = False
        self._task_cancelled = False

        # For lattice updates
        self._start_time = None
        self._end_time = None
        self._status = None
        self._error = None
        self._result = None

    @property
    def query_keys(self) -> List:
        return self._keys

    @property
    def metadata(self) -> ResultMeta:
        return self._metadata

    @property
    def assets(self):
        return self._assets

    @classmethod
    def meta_record_map(cls: DispatchedObject, key: str) -> str:
        return _meta_record_map[key]

    @property
    def start_time(self):
        return self.get_value("start_time")

    @property
    def end_time(self):
        return self.get_value("end_time")

    @property
    def dispatch_id(self):
        return self.get_value("dispatch_id")

    @property
    def root_dispatch_id(self):
        return self.get_value("root_dispatch_id")

    @property
    def status(self) -> Status:
        return self.get_value("status")

    @property
    def result(self):
        return self.get_value("result")

    @property
    def error(self):
        return self.get_value("error")

    def get_value(self, key: str, session: Session = None, refresh: bool = True):
        return get_filters[key](super().get_value(key, session, refresh))

    def set_value(self, key: str, val: Any, session: Session = None) -> None:
        super().set_value(key, set_filters[key](val), session)

    def _update_dispatch(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        status: "Status" = None,
        error: str = None,
        result: Any = None,
    ):
        """
        Update the dispatch metadata.

        Args:
            start_time: The start time of the lattice execution.
            end_time: The end time of the lattice execution.
            status: The status of the lattice execution.
            result: The lattice output unless error occured in which case None.
            error: Any error that occurred

        """

        with self.session() as session:
            if start_time is not None:
                self.set_value("start_time", start_time, session)
            if end_time is not None:
                self.set_value("end_time", end_time, session)
            if status is not None:
                self.set_value("status", status, session)
            if error is not None:
                self.set_value("error", error, session)
            if result is not None:
                self.set_value("result", result, session)

        # Copy output and error assets to sublattice's parent electron
        if RESULT_STATUS.is_terminal(status) and self._electron_id:
            with self.session() as session:
                electron_rec = Electron.get_db_records(
                    session,
                    keys=ELECTRON_KEYS,
                    equality_filters={"id": self._electron_id},
                    membership_filters={},
                )[0]
                parent_electron = Electron(session, electron_rec)

                subl_output = self.get_asset("result", session)
                subl_err = self.get_asset("error", session)
                electron_output = parent_electron.get_asset("output", session)
                electron_err = parent_electron.get_asset("error", session)

            app_log.debug("Copying sublattice output to parent electron")
            with self.session() as session:
                copy_asset_meta(session, subl_output, electron_output)
                copy_asset_meta(session, subl_err, electron_err)

            copy_asset(subl_output, electron_output)
            copy_asset(subl_err, electron_err)

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
        qelectron_data_exists: bool = None,
    ) -> bool:
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
            qelectron_data_exists: Whether the qelectron data exists.

        Returns:
            True/False indicating whether the update succeeded
        """

        app_log.debug("Inside update node")

        _start_ts = datetime.now()
        with self.session() as session:
            if status is not None:
                # This acquires a lock on the electron's row to achieve atomic RMW
                if self._can_update_node_status(session, node_id, status):
                    self.lattice.transport_graph.set_node_value(node_id, "status", status, session)
                    if status == RESULT_STATUS.COMPLETED:
                        self.incr_metadata("completed_electron_num", 1, session)
                else:
                    # Abort the update if illegal status update
                    session.rollback()
                    return False

            # Current node name
            name = self.lattice.transport_graph.get_node_value(node_id, "name", session)

            if node_name is not None:
                self.lattice.transport_graph.set_node_value(node_id, "name", node_name, session)

            if start_time is not None:
                self.lattice.transport_graph.set_node_value(
                    node_id, "start_time", start_time, session
                )

            if end_time is not None:
                self.lattice.transport_graph.set_node_value(node_id, "end_time", end_time, session)

            if output is not None:
                self.lattice.transport_graph.set_node_value(node_id, "output", output, session)

            if error is not None:
                self.lattice.transport_graph.set_node_value(node_id, "error", error, session)

            if stdout is not None:
                self.lattice.transport_graph.set_node_value(node_id, "stdout", stdout, session)

            if stderr is not None:
                self.lattice.transport_graph.set_node_value(node_id, "stderr", stderr, session)

            if qelectron_data_exists is not None:
                self.lattice.transport_graph.set_node_value(
                    node_id, "qelectron_data_exists", qelectron_data_exists, session
                )

        # Handle postprocessing node
        tg = self.lattice.transport_graph
        if name.startswith(postprocess_prefix) and end_time is not None:
            app_log.debug(f"Postprocess status: {status}")
            # Copy asset metadata
            with self.session() as session:
                workflow_result = self.get_asset("result", session)
                node_output = tg.get_node(node_id).get_asset("output", session)
                copy_asset_meta(session, node_output, workflow_result)
            copy_asset(node_output, workflow_result)

            self._update_dispatch(status=status, end_time=end_time)

        _end_ts = datetime.now()
        dt = (_end_ts - _start_ts).total_seconds()
        app_log.debug(f"_update_node took {dt} seconds")
        return True

    def _can_update_node_status(self, session: Session, node_id: int, new_status: Status) -> bool:
        """Checks whether a node status update is valid.

        The following status transitions are disallowed:
        * same-status updates e.g. completed -> completed
        * transitions from a terminal status

        In addition, a terminal status update for a sublattice electron must be consistent with the sublattice dispatch's status.

        Returns:
            bool: Whether the status update is allowed

        Side effects:
            This uses SELECT FOR UPDATE to acquire a row lock
        """

        node = self.lattice.transport_graph.get_node(node_id, session)
        node._refresh_metadata(session, for_update=True)
        old_status = node.get_value("status", session, refresh=False)
        if RESULT_STATUS.is_terminal(old_status) or old_status == new_status:
            app_log.debug(
                f"{self.dispatch_id}:{node_id}: illegal status update {old_status} -> {new_status}"
            )
            return False

        # If node is a sublattice electron, ensure that terminal
        # status updates agree with the sublattice dispatch status
        node_type = node.get_value("type", session, refresh=False)
        if node_type == "sublattice" and RESULT_STATUS.is_terminal(new_status):
            # Fetch sublattice result
            sub_dispatch_id = node.get_value("sub_dispatch_id", session, refresh=False)
            if sub_dispatch_id:
                sub_result = Result.from_dispatch_id(sub_dispatch_id, bare=True)
                if sub_result.status != new_status:
                    return False

        return True

    def _get_failed_nodes(self) -> List[int]:
        """
        Get the node_id of each failed task
        """
        return self._get_incomplete_nodes()["failed"]

    def _get_incomplete_nodes(self):
        """
        Get all nodes that did not complete.

        Returns:
            A dictionary {"failed": [node_ids], "cancelled": [node_ids]}
        """
        with self.session() as session:
            query_keys = {"id", "parent_lattice_id", "node_id", "name", "status"}
            records = Electron.get_db_records(
                session,
                keys=query_keys,
                equality_filters={"parent_lattice_id": self._id},
                membership_filters={
                    "status": [str(RESULT_STATUS.FAILED), str(RESULT_STATUS.CANCELLED)]
                },
            )

            nodes = list(map(lambda rec: Electron(session, rec, keys=query_keys), records))

            failed = list(filter(lambda e: e.get_value("status") == RESULT_STATUS.FAILED, nodes))
            cancelled = list(
                filter(lambda e: e.get_value("status") == RESULT_STATUS.CANCELLED, nodes)
            )

            failed_nodes = list(
                map(lambda x: (x.node_id, x.get_metadata("name", session, False)), failed)
            )
            cancelled_nodes = list(
                map(lambda x: (x.node_id, x.get_metadata("name", session, False)), cancelled)
            )

        return {"failed": failed_nodes, "cancelled": cancelled_nodes}

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

    def get_all_assets(self, include_nodes: bool = True) -> Dict[str, List[Asset]]:
        assets = {}

        with self.session() as session:
            lattice_records = type(self).get_linked_assets(
                session,
                fields=[],
                equality_filters={"id": self._id},
                membership_filters={},
            )
            assets["lattice"] = list(map(lambda r: r["asset"], lattice_records))
            if include_nodes:
                node_records = Electron.get_linked_assets(
                    session,
                    fields=[],
                    equality_filters={"parent_lattice_id": self._lattice_id},
                    membership_filters={},
                )
                assets["nodes"] = list(map(lambda r: r["asset"], node_records))
        return assets

    @classmethod
    def ensure_run_once(cls, dispatch_id: str) -> bool:
        """Ensure that a dispatch is only run once.


        Returns:
            bool: whether the dispatch can be run
        """
        # Atomically increment dispatch status from NEW_OBJ to STARTING
        with cls.session() as session:
            record = ResultMeta.get(
                session,
                fields=["id", "dispatch_id", "status"],
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
                for_update=True,
            )[0]
            status = get_filters["status"](record.status)

            if status == RESULT_STATUS.NEW_OBJECT:
                new_status = set_filters["status"](RESULT_STATUS.STARTING)
                ResultMeta.update_bulk(
                    session,
                    values={"status": new_status},
                    equality_filters={"dispatch_id": dispatch_id},
                    membership_filters={},
                )
                app_log.debug(f"dispatch {dispatch_id} has not been run")
                return True
            else:
                app_log.debug(f"dispatch {dispatch_id} has already been run")
                return False

    @classmethod
    def from_dispatch_id(
        cls,
        dispatch_id: str,
        bare: bool,
        *,
        session: Session = None,
        keys: list = RESULT_KEYS,
        lattice_keys: list = LATTICE_KEYS,
        electron_keys: list = ELECTRON_KEYS,
    ) -> Result:
        if session:
            records = Result.get_db_records(
                session,
                keys=keys + lattice_keys,
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            if not records:
                raise KeyError(f"Dispatch {dispatch_id} not found")

            record = records[0]

            return Result(
                session,
                record,
                bare,
                keys=keys,
                lattice_keys=lattice_keys,
                electron_keys=electron_keys,
            )
        else:
            _start_ts = datetime.now()
            with Result.session() as session:
                _lock_ts = datetime.now()
                _lock_dt = (_lock_ts - _start_ts).total_seconds()
                app_log.debug(f"Acquiring db session took {_lock_dt} seconds")
                records = Result.get_db_records(
                    session,
                    keys=keys + lattice_keys,
                    equality_filters={"dispatch_id": dispatch_id},
                    membership_filters={},
                )
                if not records:
                    raise KeyError(f"Dispatch {dispatch_id} not found")

                record = records[0]

                res = Result(
                    session,
                    record,
                    bare,
                    keys=keys,
                    lattice_keys=lattice_keys,
                    electron_keys=electron_keys,
                )

                _end_ts = datetime.now()

                dt = (_end_ts - _start_ts).total_seconds()
                app_log.debug(f"get_result_object (bare={bare}) took {dt} seconds")
                return res


def get_result_object(
    dispatch_id: str,
    bare: bool = True,
    *,
    session: Session = None,
    keys: list = RESULT_KEYS,
    lattice_keys: list = LATTICE_KEYS,
    electron_keys: list = ELECTRON_KEYS,
) -> Result:
    return Result.from_dispatch_id(
        dispatch_id,
        bare,
        session=session,
        keys=keys,
        lattice_keys=lattice_keys,
        electron_keys=electron_keys,
    )
