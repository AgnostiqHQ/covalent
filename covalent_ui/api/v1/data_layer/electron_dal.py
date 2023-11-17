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

import codecs
import pickle
import uuid
from datetime import timedelta
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import extract, select
from sqlalchemy.sql import func

from covalent._results_manager.results_manager import get_result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent.quantum.qserver.database import Database
from covalent_dispatcher._core.execution import _get_task_inputs as get_task_inputs
from covalent_ui.api.v1.data_layer.lattice_dal import Lattices
from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.models.electrons_model import JobDetailsResponse, JobsResponse
from covalent_ui.api.v1.utils.file_handle import validate_data
from covalent_ui.api.v1.utils.models_helper import JobsSortBy, SortDirection

app_log = logger.app_log
RESULTS_DIR = Path(get_config("dispatcher")["results_dir"]).resolve()


class Electrons:
    """Electron data access layer"""

    def __init__(self, db_con) -> None:
        self.db_con = db_con

    def electron_exist(self, electron_id: int) -> bool:
        return self.db_con.execute(
            select(Electron).where(Electron.transport_graph_node_id == electron_id)
        ).fetchone()

    def validate_dispatch_and_electron(
        self, dispatch_id: uuid.UUID, electron_id: int, response: JobsResponse
    ) -> (bool, JobsResponse):
        validated = True
        if not Lattices(db_con=self.db_con).dispatch_exist(dispatch_id=dispatch_id):
            validated = False
            response.data = None
            response.msg = f"Dispatch ID {dispatch_id} does not exist"
            return (validated, response)
        if not self.electron_exist(electron_id=electron_id):
            validated = False
            response.data = None
            response.msg = f"Electron ID {electron_id} does not exist"
            return (validated, response)

        return (validated, response)

    def get_jobs(
        self,
        dispatch_id: uuid.UUID,
        electron_id: int,
        sort_by: JobsSortBy,
        sort_direction: SortDirection,
        count,
        offset,
    ) -> JobsResponse:
        try:
            jobs_response = JobsResponse()
            jobs_response.data = None
            jobs_response.msg = None
            (validated, jobs_response) = self.validate_dispatch_and_electron(
                dispatch_id=dispatch_id, electron_id=electron_id, response=jobs_response
            )
            if not validated:
                return jobs_response
            try:
                jobs = self._get_qelectron_db_dict(str(dispatch_id), electron_id)
                if len(jobs) == 0:
                    jobs_response.data = []
                    jobs_response.msg = f"Job details for {dispatch_id} dispatch with {electron_id} node do not exist."
                    return jobs_response
            except Exception as exc:
                app_log.debug(f"Unable to process get jobs \n {exc}")
                jobs_response.data = []
                jobs_response.msg = (
                    f"Jobs for {dispatch_id} dispatch with {electron_id} node do not exist."
                )
                return jobs_response
            jobs_list = list(
                map(
                    lambda circuit: {
                        "job_id": circuit["circuit_id"],
                        "start_time": circuit["save_time"],
                        "executor": circuit["result_metadata"]["executor_name"],
                        "status": "COMPLETED"
                        if len(circuit["result"]) != 0 and len(circuit["result_metadata"]) != 0
                        else "RUNNING",
                    },
                    jobs.values(),
                )
            )
            jobs_list.sort(
                reverse=sort_direction == SortDirection.DESCENDING, key=lambda d: d[sort_by.value]
            )
            result = (
                jobs_list[offset : count + offset] if count is not None else jobs_list[offset:]
            )

            jobs_response.data = result
            return jobs_response
        except Exception as exc:
            app_log.debug(f"Unable to process get jobs \n {exc}")
            jobs_response.msg = "Something went wrong. Please check the log."
            jobs_response.data = None
            return jobs_response

    def get_job_detail(self, dispatch_id, electron_id, job_id) -> JobDetailsResponse:
        try:
            job_detail_response = JobDetailsResponse()
            job_detail_response.data = None
            job_detail_response.msg = None
            (validated, job_detail_response) = self.validate_dispatch_and_electron(
                dispatch_id=dispatch_id, electron_id=electron_id, response=job_detail_response
            )
            if not validated:
                return job_detail_response
            try:
                jobs = self._get_qelectron_db_dict(
                    dispatch_id=str(dispatch_id), node_id=electron_id
                )
                selected_job = jobs[job_id]
            except Exception as exc:
                app_log.debug(f"Unable to process get jobs \n {exc}")
                job_detail_response.data = []
                job_detail_response.msg = (
                    f"Job details for {dispatch_id} dispatch with {electron_id} node do not exist."
                )
                return job_detail_response
            if not selected_job:
                job_detail_response.data = {}
                job_detail_response.msg = (
                    f"Dispatch ID {dispatch_id} or Electron ID does not exist"
                )
                return job_detail_response
            if "result" not in selected_job:
                job_detail_response.data = {}
                job_detail_response.msg = (
                    f"Dispatch ID {dispatch_id} or Electron ID does not exist"
                )
                return job_detail_response
            selected_job["result"] = str(selected_job["result"])[1:-1]
            job_overview = {
                "overview": {
                    "job_name": selected_job["circuit_name"]
                    if "circuit_name" in selected_job
                    else None,
                    "backend": selected_job["result_metadata"]["executor_backend_name"]
                    if "result_metadata" in selected_job
                    and "executor_backend_name" in selected_job["result_metadata"]
                    else None,
                    "time_elapsed": selected_job["execution_time"]
                    if "execution_time" in selected_job
                    else None,
                    "result": selected_job["result"] if "result" in selected_job else None,
                    "status": "COMPLETED"
                    if len(selected_job["result"]) != 0
                    and len(selected_job["result_metadata"]) != 0
                    else "RUNNING",
                    "start_time": selected_job["save_time"]
                    if "save_time" in selected_job
                    else None,
                },
                "circuit": {
                    "total_qbits": None,
                    "depth": None,
                    "circuit_diagram": selected_job["circuit_diagram"]
                    if "circuit_diagram" in selected_job
                    else None,
                },
                "executor": {
                    "name": selected_job["qexecutor"]["name"]
                    if "qexecutor" in selected_job and "name" in selected_job["qexecutor"]
                    else None,
                    "executor": str(selected_job["qexecutor"])
                    if "qexecutor" in selected_job
                    else None,
                },
            }

            job_overview["overview"]["end_time"] = (
                selected_job["save_time"] + timedelta(seconds=selected_job["execution_time"])
                if job_overview["overview"]["start_time"]
                and job_overview["overview"]["time_elapsed"]
                else None
            )
            if selected_job["qnode_specs"] is not None:
                job_overview["circuit"]["total_qbits"] = (
                    selected_job["qnode_specs"]["num_used_wires"]
                    if "num_used_wires" in selected_job["qnode_specs"]
                    else None
                )
                job_overview["circuit"]["depth"] = (
                    selected_job["qnode_specs"]["depth"]
                    if "depth" in selected_job["qnode_specs"]
                    else None
                )
                gate_sizes = (
                    selected_job["qnode_specs"]["gate_sizes"]
                    if "gate_sizes" in selected_job["qnode_specs"]
                    else None
                )
                if gate_sizes:
                    for gate_wires, gate_count in gate_sizes.items():
                        job_overview["circuit"][f"qbit{gate_wires}_gates"] = gate_count

            job_detail_response.data = job_overview
            job_detail_response.msg = ""
            return job_detail_response
        except Exception as exc:
            app_log.debug(f"Unable to process get job details \n {exc}")
            job_detail_response.msg = "Something went wrong. Please check the log."
            job_detail_response.data = None
            return job_detail_response

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
                Electron.executor_data,
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
                        func.coalesce(
                            extract("epoch", Electron.completed_at),
                            extract("epoch", func.now()),
                        )
                        - extract("epoch", Electron.started_at)
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

    def get_total_quantum_calls(self, dispatch_id, node_id):
        qdb = self._get_qelectron_db_dict(dispatch_id=str(dispatch_id), node_id=node_id)
        return None if len(qdb) == 0 else len(qdb)

    def get_avg_quantum_calls(self, dispatch_id, node_id):
        jobs = self._get_qelectron_db_dict(dispatch_id=str(dispatch_id), node_id=node_id)
        if len(jobs) == 0:
            return None

        time = [jobs[value]["execution_time"] for value in jobs]
        return sum(time) / len(time)

    def get_electron_inputs(self, dispatch_id: uuid.UUID, electron_id: int) -> str:
        """
        Get Electron Inputs
        Args:
            dispatch_id: Dispatch id of lattice/sublattice
            electron_id: Transport graph node id of a electron
        Returns:
            Returns the inputs data from Result object
        """

        result = get_result(dispatch_id=str(dispatch_id), wait=False)
        if isinstance(result, JSONResponse) and result.status_code == 404:
            raise HTTPException(status_code=400, detail=result)
        result_object = pickle.loads(codecs.decode(result["result"].encode(), "base64"))
        electron_result = self.get_electrons_id(dispatch_id, electron_id)
        inputs = get_task_inputs(
            node_id=electron_id, node_name=electron_result.name, result_object=result_object
        )
        return validate_data(inputs)

    def _get_qelectron_db_dict(self, dispatch_id: str, node_id: int) -> dict:
        """Return the QElectron DB for a given node."""

        electron = self.get_electrons_id(dispatch_id, node_id)

        database = Database(electron.storage_path)
        qelectron_db_dict = database.get_db_dict(
            dispatch_id=dispatch_id, node_id=node_id, direct_path=True
        )

        return qelectron_db_dict
