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

"""Lattice route"""

import uuid

from fastapi import APIRouter
from sqlalchemy.orm import Session

from covalent_ui.app.api_v0.data_layer.lattice_dal import Lattices
from covalent_ui.app.api_v0.database.config.db import engine
from covalent_ui.app.api_v0.models.file_model import FileMapper, Filetype
from covalent_ui.app.api_v0.models.lattices_model import (
    FileOutput,
    LatticeDetailResponse,
    LatticeExecutorResponse,
    LatticeFileResponse,
)
from covalent_ui.app.api_v0.utils.file_handle import FileHandler

routes: APIRouter = APIRouter()


@routes.get("/{dispatch_id}", response_model=LatticeDetailResponse)
def get_lattice_details(dispatch_id: uuid.UUID):
    """Get lattice details

    Args:
        dispatch_id: To fetch lattice data with the provided dispatch id

    Returns:
        Returns the lattice data with the dispatch id provided
    """

    with Session(engine) as session:
        electron = Lattices(session)
        data = electron.get_lattices_id(dispatch_id)
        if data[0] is not None:
            return LatticeDetailResponse(
                dispatch_id=data.dispatch_id,
                status=data.status,
                total_electrons=data.total_electrons,
                total_electrons_completed=data.total_electrons_completed,
                start_time=data.start_time,
                end_time=data.end_time,
                directory=data.directory,
            )
        return LatticeDetailResponse(
            dispatch_id=None,
            status=None,
            run_time=None,
            total_electrons=None,
            total_electrons_completed=None,
            start_time=None,
            end_time=None,
            directory=None,
        )


@routes.get("/{dispatch_id}/details/{name}")
def get_lattice_files(dispatch_id: uuid.UUID, name: FileOutput):
    """Get lattice file data

    Args:
        dispatch_id: To fetch lattice data with the provided dispatch id
        name: To fetch specific file data for a lattice

    Returns:
        Returns the lattice file data with the dispatch id and file_module provided provided
    """
    with Session(engine) as session:
        electron = Lattices(session)
        data = electron.get_lattices_id_storage_file(dispatch_id)
        file_module_name = int(FileMapper[name.name].value)
        # return True
        if data[0] is not None:
            executor_file_path = f"{data[2]}/"
            print(executor_file_path)
            print(data[file_module_name])
            results = FileHandler.file_read(executor_file_path, data[file_module_name])
            if file_module_name != Filetype.FUNCTION_STRING.value:
                if name.value == FileOutput.RESULT.value:
                    if results is None:
                        return LatticeFileResponse(data=f"{results}")
                    return LatticeFileResponse(data=f"{results.result}")
                if name.value == FileOutput.INPUTS.value:
                    converter = str(f"{results}")
                    return LatticeFileResponse(
                        data=converter.replace(":", "=").replace("{", "").replace("}", "")
                    )
                if (
                    name.value == FileOutput.FUNCTION_STRING.value
                    or name.value == FileOutput.ERROR.value
                ):
                    return LatticeFileResponse(data=results)
                return LatticeExecutorResponse(data=results, executor_name=data)
            return LatticeFileResponse(data=results)
        return LatticeFileResponse(data=None)
