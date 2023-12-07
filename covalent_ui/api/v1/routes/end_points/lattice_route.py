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

"""Lattice route"""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Path, Query
from sqlalchemy.orm import Session

import covalent_ui.api.v1.database.config.db as db
from covalent_ui.api.v1.data_layer.lattice_dal import Lattices
from covalent_ui.api.v1.models.dispatch_model import SortDirection
from covalent_ui.api.v1.models.lattices_model import (
    LatticeDetailResponse,
    LatticeExecutorResponse,
    LatticeFileOutput,
    LatticeFileResponse,
    LatticeWorkflowExecutorResponse,
    SubLatticeDetailResponse,
    SubLatticeSortBy,
)
from covalent_ui.api.v1.utils.file_handle import FileHandler

routes: APIRouter = APIRouter()


@routes.get("/{dispatch_id}", response_model=LatticeDetailResponse)
def get_lattice_details(dispatch_id: uuid.UUID):
    """Get lattice details

    Args:
        dispatch_id: To fetch lattice data with the provided dispatch id

    Returns:
        Returns the lattice data with the dispatch id provided
    """

    with Session(db.engine) as session:
        lattice = Lattices(session)
        data = lattice.get_lattices_id(dispatch_id)
        if data is not None:
            handler = FileHandler(data["directory"])
            return LatticeDetailResponse(
                dispatch_id=data.dispatch_id,
                status=data.status,
                total_electrons=data.total_electrons,
                total_electrons_completed=data.total_electrons_completed,
                started_at=data.start_time,
                ended_at=data.end_time,
                directory=data.directory,
                description=handler.read_from_text(data.docstring_filename),
                runtime=data.runtime,
            )
        raise HTTPException(
            status_code=400,
            detail=[
                {
                    "loc": ["path", "dispatch_id"],
                    "msg": f"Dispatch ID {dispatch_id} does not exist",
                    "type": None,
                }
            ],
        )


@routes.get("/{dispatch_id}/details/{name}")
def get_lattice_files(dispatch_id: uuid.UUID, name: LatticeFileOutput):
    """Get lattice file data

    Args:
        dispatch_id: To fetch lattice data with the provided dispatch id
        name: To fetch specific file data for a lattice

    Returns:
        Returns the lattice file data with the dispatch id and file_module provided provided
    """
    with Session(db.engine) as session:
        lattice = Lattices(session)
        lattice_data = lattice.get_lattices_id_storage_file(dispatch_id)

        if lattice_data is None:
            raise HTTPException(
                status_code=400,
                detail=[
                    {
                        "loc": ["path", "dispatch_id"],
                        "msg": f"Dispatch ID {dispatch_id} does not exist",
                        "type": None,
                    }
                ],
            )

        handler = FileHandler(lattice_data["directory"])
        if name == "result":
            response, python_object = handler.read_from_serialized(
                lattice_data["results_filename"]
            )
            return LatticeFileResponse(data=str(response), python_object=python_object)

        if name == "inputs":
            response, python_object = handler.read_from_serialized(lattice_data["inputs_filename"])
            return LatticeFileResponse(data=response, python_object=python_object)

        elif name == "function_string":
            response = handler.read_from_text(lattice_data["function_string_filename"])
            return LatticeFileResponse(data=response)

        elif name == "executor":
            executor_name = lattice_data["executor"]
            executor_data = json.loads(lattice_data["executor_data"])

            return LatticeExecutorResponse(
                executor_name=executor_name, executor_details=executor_data
            )

        elif name == "workflow_executor":
            executor_name = lattice_data["workflow_executor"]
            executor_data = json.loads(lattice_data["workflow_executor_data"])

            return LatticeWorkflowExecutorResponse(
                workflow_executor_name=executor_name, workflow_executor_details=executor_data
            )

        elif name == "error":
            response = handler.read_from_text(lattice_data["error_filename"])
            return LatticeFileResponse(data=response)

        elif name == "function":
            response, python_object = handler.read_from_serialized(
                lattice_data["function_filename"]
            )
            return LatticeFileResponse(data=response, python_object=python_object)

        else:
            return LatticeFileResponse(data=None)


@routes.get("/{dispatch_id}/sublattices", response_model=SubLatticeDetailResponse)
def get_sub_lattice(
    sort_by: Optional[SubLatticeSortBy] = Query(default=SubLatticeSortBy.RUNTIME),
    sort_direction: Optional[SortDirection] = Query(default=SortDirection.DESCENDING),
    dispatch_id: uuid.UUID = Path(title="dispatch id"),
):
    """Get All Sub Lattices

    Args:
        req: Dispatch ID

    Returns:
        List of Sub Lattices details
    """
    with Session(db.engine) as session:
        lattice = Lattices(session)
        data = lattice.get_sub_lattice_details(
            dispatch_id=dispatch_id, sort_by=sort_by, sort_direction=sort_direction
        )
        return SubLatticeDetailResponse(sub_lattices=data)
