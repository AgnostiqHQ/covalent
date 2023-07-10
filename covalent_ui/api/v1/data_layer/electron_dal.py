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

from datetime import timedelta, timezone
from uuid import UUID

from sqlalchemy.sql import func

from covalent.experimental.covalent_qelectron.quantum_server.database import Database
from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.utils.models_helper import JobsSortBy, SortDirection


class Electrons:
    """Electron data access layer"""

    def __init__(self, db_con) -> None:
        self.db_con = db_con
        self.qdb = Database()

    def get_jobs(
        self,
        dispatch_id: UUID,
        electron_id: int,
        sort_by: JobsSortBy,
        sort_direction: SortDirection,
        count,
        offset,
    ):
        try:
            jobs = self.qdb.get_db(dispatch_id=str(dispatch_id), node_id=electron_id)
            jobs_list = [
                {
                    "job_id": circuit["circuit_id"],
                    "start_time": circuit["save_time"],
                    "executor": circuit["result_metadata"]["executor_name"],
                    "status": "COMPLETED"
                    if len(circuit["result"]) != 0 and len(circuit["result_metadata"]) != 0
                    else "RUNNING",
                }
                for _, circuit in jobs.items()
            ]
            jobs_list.sort(
                reverse=sort_direction == SortDirection.DESCENDING, key=lambda d: d[sort_by.value]
            )
            result = (
                jobs_list[offset: count + offset] if count is not None else jobs_list[offset:]
            )
            return result
        except:
            return None

    def get_job_detail(self, dispatch_id, electron_id, job_id):
        try:
            selected_job = self.qdb.get_db(
                dispatch_id=str(dispatch_id),
                node_id=electron_id)[job_id]
            selected_job["result"] = str(selected_job["result"])[1:-1]
            job_overview = {
                "overview": {
                    "job_name": selected_job["circuit_name"] if "circuit_name" in selected_job else None,
                    "backend": selected_job["result_metadata"]["executor_backend_name"]
                    if "result_metadata" in selected_job and "executor_backend_name" in selected_job["result_metadata"] else None,
                    "time_elapsed": selected_job["execution_time"] if "execution_time" in selected_job else None,
                    "result": selected_job["result"] if "result" in selected_job else None,
                    "status": "COMPLETED"
                    if len(selected_job["result"]) != 0
                    and len(selected_job["result_metadata"]) != 0
                    else "RUNNING",
                    "start_time": selected_job["save_time"]if "save_time" in selected_job else None,
                    "end_time": selected_job["save_time"]
                    + timedelta(seconds=selected_job["execution_time"]),
                },
                "circuit": {
                    "total_qbits": None,
                    "qbit1_gates": None,
                    "qbit2_gates": None,
                    "depth": None,
                    "circuit_diagram": selected_job["circuit_diagram"],
                },
                "executor": {
                    "name": selected_job["qexecutor"]["name"] if "qexecutor" in selected_job and "name" in selected_job["qexecutor"] else None,
                    "executor": selected_job["qexecutor"] if "qexecutor" in selected_job else None,
                },
            }
            if selected_job["qnode_specs"] != None:
                job_overview["circuit"]["total_qbits"] = selected_job["qnode_specs"]["num_used_wires"]
                job_overview["circuit"]["depth"] = selected_job["qnode_specs"]["depth"]
                gate_sizes = selected_job["qnode_specs"]["gate_sizes"]
                if gate_sizes != None:
                    job_overview["circuit"]["qbit1_gates"] = gate_sizes["1"]
                    job_overview["circuit"]["qbit2_gates"] = gate_sizes["2"]
            return job_overview
        except:
            return None

    def get_electrons_id(self, dispatch_id, electron_id) -> Electron:
        """
        Read electron table by electron id
        Args:
            electron_id: Refers to the electron's PK
        Return:
            Electron with PK as electron_id
        """
        data = (
            self.db_con.query(
                Electron.id,
                Electron.transport_graph_node_id,
                Electron.parent_lattice_id,
                Electron.type,
                Electron.storage_path,
                Electron.function_filename,
                Electron.function_string_filename,
                Electron.executor,
                Electron.executor_data_filename,
                Electron.results_filename,
                Electron.value_filename,
                Electron.stdout_filename,
                Electron.deps_filename,
                Electron.call_before_filename,
                Electron.call_after_filename,
                Electron.stderr_filename,
                Electron.error_filename,
                Electron.name,
                Electron.status,
                Electron.job_id,
                Electron.qelectron_data_exists,
                Electron.started_at.label("started_at"),
                Electron.completed_at.label("completed_at"),
                (
                    (
                        func.strftime(
                            "%s",
                            func.IFNULL(Electron.completed_at, func.datetime.now(timezone.utc)),
                        )
                        - func.strftime("%s", Electron.started_at)
                    )
                    * 1000
                ).label("runtime"),
            )
            .join(Lattice, Lattice.id == Electron.parent_lattice_id)
            .filter(
                Lattice.dispatch_id == str(dispatch_id),
                Electron.transport_graph_node_id == electron_id,
            )
            .first()
        )
        return data

    def get_total_quantum_calls(self, dispatch_id, node_id, is_qa_electron: bool):
        if not is_qa_electron:
            return None
        return len(self.qdb.get_circuit_ids(dispatch_id=str(dispatch_id), node_id=node_id))

    def get_avg_quantum_calls(self, dispatch_id, node_id, is_qa_electron: bool):
        if not is_qa_electron:
            return None
        jobs = self.qdb.get_db(dispatch_id=str(dispatch_id), node_id=node_id)
        time = [jobs[value]["execution_time"] for value in jobs]
        return sum(time) / len(time)
