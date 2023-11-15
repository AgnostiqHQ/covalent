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

import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

import covalent_ui.api.v1.database.config.db as db
from covalent._shared_files.defaults import WAIT_EDGE_NAME
from covalent_dispatcher._core.data_modules import graph as core_graph
from covalent_dispatcher._dal.result import get_result_object
from covalent_ui.api.v1.data_layer.electron_dal import Electrons
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
    with Session(db.engine) as session:
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
                dispatch_id,
                result["transport_graph_node_id"],
            ),
            "avg_quantum_calls": electron.get_avg_quantum_calls(
                dispatch_id=dispatch_id,
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
            qelectron_data_exists=qelectron["total_quantum_calls"] is not None,
            qelectron=qelectron if qelectron["total_quantum_calls"] is not None else None,
        )


def _get_abstract_task_inputs(dispatch_id: str, node_id: int) -> dict:
    """Return placeholders for the required inputs for a task execution.

    Args:
        dispatch_id: id of the current dispatch
        node_id: Node id of this task in the transport graph.
        node_name: Name of the node.

    Returns: inputs: Input dictionary to be passed to the task with
        `node_id` placeholders for args, kwargs. These are to be
        resolved to their values later.
    """

    abstract_task_input = {"args": [], "kwargs": {}}

    in_edges = core_graph.get_incoming_edges_sync(dispatch_id, node_id)
    for edge in in_edges:
        parent = edge["source"]

        d = edge["attrs"]

        if d["edge_name"] != WAIT_EDGE_NAME:
            if d["param_type"] == "arg":
                abstract_task_input["args"].append((parent, d["arg_index"]))
            elif d["param_type"] == "kwarg":
                key = d["edge_name"]
                abstract_task_input["kwargs"][key] = parent

    sorted_args = sorted(abstract_task_input["args"], key=lambda x: x[1])
    abstract_task_input["args"] = [x[0] for x in sorted_args]

    return abstract_task_input


# Domain: data
def get_electron_inputs(dispatch_id: uuid.UUID, electron_id: int) -> str:
    """
    Get Electron Inputs
    Args:
        dispatch_id: Dispatch id of lattice/sublattice
        electron_id: Transport graph node id of a electron
    Returns:
        Returns the inputs data from Result object
    """

    abstract_inputs = _get_abstract_task_inputs(dispatch_id=str(dispatch_id), node_id=electron_id)

    # Resolve node ids to object strings
    input_assets = {"args": [], "kwargs": {}}

    with Session(db.engine) as session:
        result_object = get_result_object(str(dispatch_id), bare=True)
        tg = result_object.lattice.transport_graph
        for arg in abstract_inputs["args"]:
            node = tg.get_node(node_id=arg, session=session)
            asset = node.get_asset(key="output", session=session)
            input_assets["args"].append(asset)
        for k, v in abstract_inputs["kwargs"].items():
            node = tg.get_node(node_id=v, session=session)
            asset = node.get_asset(key="output", session=session)
            input_assets["kwargs"][k] = asset

    # For now we load the picklefile from the object store into memory, but once
    # TransportableObjects are no longer pickled we will be
    # able to load the byte range for the object string.
    input_args = [asset.load_data() for asset in input_assets["args"]]
    input_kwargs = {k: asset.load_data() for k, asset in input_assets["kwargs"].items()}
    return validate_data({"args": input_args, "kwargs": input_kwargs})


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

    with Session(db.engine) as session:
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
            response, python_object = handler.read_from_serialized(result["function_filename"])
            return ElectronFileResponse(data=response, python_object=python_object)
        elif name == "executor":
            executor_name = result["executor"]
            executor_data = json.loads(result["executor_data"])
            return ElectronExecutorResponse(
                executor_name=executor_name, executor_details=executor_data
            )
        elif name == "result":
            response, python_object = handler.read_from_serialized(result["results_filename"])
            return ElectronFileResponse(data=str(response), python_object=python_object)
        elif name == "value":
            response = handler.read_from_serialized(result["value_filename"])
            return ElectronFileResponse(data=str(response))
        elif name == "stdout":
            response = handler.read_from_text(result["stdout_filename"])
            return ElectronFileResponse(data=response)
        elif name == "deps":
            response = handler.read_from_serialized(result["deps_filename"])
            return ElectronFileResponse(data=response)
        elif name == "call_before":
            response = handler.read_from_serialized(result["call_before_filename"])
            return ElectronFileResponse(data=response)
        elif name == "call_after":
            response = handler.read_from_serialized(result["call_after_filename"])
            return ElectronFileResponse(data=response)
        elif name == "error":
            # Error and stderr won't be both populated if `error`
            # is only used for fatal dispatcher-executor interaction errors
            error_response = handler.read_from_text(result["error_filename"])
            stderr_response = handler.read_from_text(result["stderr_filename"])
            response = stderr_response + error_response
            return ElectronFileResponse(data=response)
        elif name == "qelectron_db":
            # Since in case of bytes 2 same bytes objects are returned by the handler
            # so we are taking only the first one
            response = handler.read_from_serialized(result["qelectron_db_filename"])[0]
            return ElectronFileResponse(data=response)
        else:
            return ElectronFileResponse(data=None)


@routes.get("/{dispatch_id}/electron/{electron_id}/jobs", response_model=List[Job])
def get_electron_jobs(
    dispatch_id: uuid.UUID,
    electron_id: int,
    sort_by: Optional[JobsSortBy] = JobsSortBy.START_TIME,
    sort_direction: Optional[SortDirection] = SortDirection.DESCENDING,
    count: Optional[int] = None,
    offset: Optional[int] = Query(0),
) -> List[Job]:
    """Get Qelectron Jobs List

    Args:
        dispatch_id: To fetch qelectron data with dispatch id
        electron_id: To fetch qelectron data with the provided electron id.

    Returns:
        Returns the list of qelectron jobs
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
