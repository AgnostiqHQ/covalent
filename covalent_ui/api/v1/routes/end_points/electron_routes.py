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

"""Electrons Route"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

import covalent_ui.api.v1.database.config.db as db
from covalent._results_manager.results_manager import get_result
from covalent_dispatcher._core.execution import _get_task_inputs as get_task_inputs
from covalent_ui.api.v1.data_layer.electron_dal import Electrons
from covalent_ui.api.v1.database.config.db import engine
from covalent_ui.api.v1.models.electrons_model import (
    ElectronExecutorResponse,
    ElectronFileOutput,
    ElectronFileResponse,
    ElectronResponse,
    Job,
    JobDetails,
    JobDetailsResponse,
    JobsResponse,
)
from covalent_ui.api.v1.utils.file_handle import FileHandler, validate_data
from covalent_ui.api.v1.utils.models_helper import JobsSortBy, SortDirection

routes: APIRouter = APIRouter()


@routes.get("/{dispatch_id}/electron/{electron_id}", response_model=ElectronResponse)
def get_electron_details(dispatch_id: uuid.UUID, electron_id: int):
    """Get Electron Details

    Args:
        electron_id: To fetch electron data with the provided electron id.

    Returns:
        Returns the electron details
    """
    with Session(engine) as session:
        electron = Electrons(session)
        result = electron.get_electrons_id(dispatch_id, electron_id)
        if result is None:
            raise HTTPException(
                status_code=400,
                detail=[
                    {
                        "loc": ["path", "dispatch_id"],
                        "msg": f"Dispatch ID {dispatch_id} or Electron ID does not exist",
                        "type": None,
                    }
                ],
            )
        qelectron = {
            "total_quantum_calls": electron.get_total_quantum_calls(
                dispatch_id, result["transport_graph_node_id"], result["qelectron_data_exists"]
            ),
            "avg_quantum_calls": electron.get_avg_quantum_calls(
                dispatch_id=dispatch_id,
                is_qa_electron=result["qelectron_data_exists"],
                node_id=result["transport_graph_node_id"],
            ),
        }
        return ElectronResponse(
            id=result["id"],
            node_id=result["transport_graph_node_id"],
            parent_lattice_id=result["parent_lattice_id"],
            type=result["type"],
            storage_path=result["storage_path"],
            name=result["name"],
            status=result["status"],
            started_at=result["started_at"],
            ended_at=result["completed_at"],
            runtime=result["runtime"],
            description="",
            qelectron_data_exists=bool(result["qelectron_data_exists"]),
            qelectron=qelectron if bool(result["qelectron_data_exists"]) else None,
        )


def get_electron_inputs(dispatch_id: uuid.UUID, electron_id: int) -> str:
    """
    Get Electron Inputs
    Args:
        dispatch_id: Dispatch id of lattice/sublattice
        electron_id: Transport graph node id of a electron
    Returns:
        Returns the inputs data from Result object
    """

    result_object = get_result(dispatch_id=str(dispatch_id), wait=False)

    with Session(engine) as session:
        electron = Electrons(session)
        result = electron.get_electrons_id(dispatch_id, electron_id)
        inputs = get_task_inputs(
            node_id=electron_id, node_name=result.name, result_object=result_object
        )
        return validate_data(inputs)


@routes.get("/{dispatch_id}/electron/{electron_id}/details/{name}")
def get_electron_file(dispatch_id: uuid.UUID, electron_id: int, name: ElectronFileOutput):
    """
    Get Electron details
    Args:
        dispatch_id: Dispatch id of lattice/sublattice
        electron_id: Transport graph node id of a electron
        name: refers file type, like inputs, function_string, function, executor, result, value, key,
        stdout, deps, call_before, call_after, error, info
    Returns:
        Returns electron details based on the given name
    """

    with Session(engine) as session:
        electron = Electrons(session)
        result = electron.get_electrons_id(dispatch_id, electron_id)
        if result is not None:
            handler = FileHandler(result["storage_path"])
            if name == "inputs":
                response, python_object = get_electron_inputs(
                    dispatch_id=dispatch_id, electron_id=electron_id
                )
                return ElectronFileResponse(data=str(response), python_object=str(python_object))
            elif name == "function_string":
                response = handler.read_from_text(result["function_string_filename"])
                return ElectronFileResponse(data=response)
            elif name == "function":
                response, python_object = handler.read_from_pickle(result["function_filename"])
                return ElectronFileResponse(data=response, python_object=python_object)
            elif name == "executor":
                executor_name = result["executor"]
                executor_data = handler.read_from_pickle(result["executor_data_filename"])
                return ElectronExecutorResponse(
                    executor_name=executor_name, executor_details=executor_data
                )
            elif name == "result":
                response, python_object = handler.read_from_pickle(result["results_filename"])
                return ElectronFileResponse(data=str(response), python_object=python_object)
            elif name == "value":
                response = handler.read_from_pickle(result["value_filename"])
                return ElectronFileResponse(data=str(response))
            elif name == "stdout":
                response = handler.read_from_text(result["stdout_filename"])
                return ElectronFileResponse(data=response)
            elif name == "deps":
                response = handler.read_from_pickle(result["deps_filename"])
                return ElectronFileResponse(data=response)
            elif name == "call_before":
                response = handler.read_from_pickle(result["call_before_filename"])
                return ElectronFileResponse(data=response)
            elif name == "call_after":
                response = handler.read_from_pickle(result["call_after_filename"])
                return ElectronFileResponse(data=response)
            elif name == "error":
                # Error and stderr won't be both populated if `error`
                # is only used for fatal dispatcher-executor interaction errors
                error_response = handler.read_from_text(result["error_filename"])
                stderr_response = handler.read_from_text(result["stderr_filename"])
                response = stderr_response + error_response
                return ElectronFileResponse(data=response)
            else:
                return ElectronFileResponse(data=None)
        else:
            raise HTTPException(
                status_code=400,
                detail=[
                    {
                        "loc": ["path", "dispatch_id"],
                        "msg": f"Dispatch ID {dispatch_id} or Electron ID does not exist",
                        "type": None,
                    }
                ],
            )


@routes.get("/{dispatch_id}/electron/{electron_id}/jobs", response_model=List[Job])
def get_electron_jobs(
    dispatch_id: uuid.UUID,
    electron_id: int,
    sort_by: Optional[JobsSortBy] = JobsSortBy.START_TIME,
    sort_direction: Optional[SortDirection] = SortDirection.DESCENDING,
    count: Optional[int] = None,
    offset: Optional[int] = Query(0),
) -> List[Job]:
    """Get Electron Jobs List

    Args:
        dispatch_id: To fetch electron data with dispatch id
        electron_id: To fetch electron data with the provided electron id.

    Returns:
        Returns the list of electron jobs
    """
    with Session(db.engine) as session:
        electron = Electrons(session)
        jobs_response: JobsResponse = electron.get_jobs(
            dispatch_id=dispatch_id,
            electron_id=electron_id,
            sort_by=sort_by,
            sort_direction=sort_direction,
            count=count,
            offset=offset,
        )
        if jobs_response.data is None:
            raise HTTPException(
                status_code=422,
                detail=[{"msg": jobs_response.msg}],
            )
        return jobs_response.data


@routes.get("/{dispatch_id}/electron/{electron_id}/jobs/{job_id}", response_model=JobDetails)
def get_electron_job_overview(dispatch_id: uuid.UUID, electron_id: int, job_id: str) -> JobDetails:
    """Get Electron Job Detail

    Args:
        dispatch_id: To fetch electron data with dispatch id
        electron_id: To fetch electron data with the provided electron id.
        job_id: To fetch appropriate job details with job id

    Returns:
        Returns the electron job details
    """
    with Session(db.engine) as session:
        electron = Electrons(session)
        job_response: JobDetailsResponse = electron.get_job_detail(
            dispatch_id, electron_id, job_id
        )
        if job_response.data is None:
            raise HTTPException(
                status_code=422,
                detail=[{"msg": job_response.msg}],
            )

        return job_response.data
