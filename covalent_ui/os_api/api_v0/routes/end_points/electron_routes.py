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
# Relief from the License may be granted by purchasing a commercial license.

"""Electrons Route"""

import uuid
from enum import Enum
from random import randrange

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from covalent_ui.os_api.api_v0.data_layer.electron_dal import Electrons
from covalent_ui.os_api.api_v0.database.config.db import engine
from covalent_ui.os_api.api_v0.database.lattice_file_mock import file_read
from covalent_ui.os_api.api_v0.models.electrons_model import FileOutput
from covalent_ui.os_api.api_v0.models.lattices_model import (
    ElectronExecutorResponse,
    ElectronFileResponse,
    ElectronResponse,
)

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
            raise HTTPException(status_code=400, detail=[f"{dispatch_id} does not exists"])
        return ElectronResponse(
            item={
                "id": result[0],
                "transport_graph_node_id": result[1],
                "parent_lattice_id": result[2],
                "type": result[3],
                "storage_path": result[4],
                "name": result[5],
                "status": result[6],
                "started_at": result[7],
                "ended_at": result[8],
            }
        )


@routes.get("/{dispatch_id}/electron/{electron_id}/details/{name}")
def get_electron_file(dispatch_id: uuid.UUID, electron_id: int, name: FileOutput):
    with Session(engine) as session:
        electron = Electrons(session)
        result = electron.get_electrons_id(dispatch_id, electron_id)
        if result is None:
            raise HTTPException(status_code=400, detail=[f"{dispatch_id} does not exists"])
        if name in ["result", "inputs"]:
            response = file_read()
            return ElectronFileResponse(data=str(response[name]))
        elif name == "function_string":
            response = file_read()
            return ElectronFileResponse(data=response[name][randrange(3)])
        elif name == "executor_details":
            response = file_read()
            return ElectronExecutorResponse(data=response[name], executor_name="dask")
        response = file_read()
        return ElectronFileResponse(data=response[name])
