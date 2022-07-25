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
from covalent_ui.os_api.api_v0.utils.file_handle import FileHandler

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
            id=result["id"],
            node_id=result["transport_graph_node_id"],
            parent_lattice_id=result["parent_lattice_id"],
            type=result["type"],
            storage_path=result["storage_path"],
            name=result["name"],
            status=result["status"],
            started_at=result["started_at"],
            ended_at=result["completed_at"],
        )


@routes.get("/{dispatch_id}/electron/{electron_id}/details/{name}")
def get_electron_file(dispatch_id: uuid.UUID, electron_id: int, name: FileOutput):
    with Session(engine) as session:
        electron = Electrons(session)
        result = electron.get_electrons_id(dispatch_id, electron_id)
        if result[0] is not None:
            handler = FileHandler(result["storage_path"])
            if name == "function_string":
                response = handler.read_from_text(result["function_string_filename"])
                return ElectronFileResponse(data=response)
            elif name == "function":
                response = handler.read_from_pickle(result["function_filename"])
                return ElectronFileResponse(data=response)
            elif name == "executor_details":
                response = handler.read_from_pickle(result["executor_filename"])
                return ElectronExecutorResponse(data=response, executor_name="dask")
            elif name == "result":
                response = handler.read_from_pickle(result["results_filename"])
                return ElectronFileResponse(data=str(response))
            elif name == "value":
                response = handler.read_from_pickle(result["value_filename"])
                return ElectronFileResponse(data=response)
            elif name == "key":
                response = handler.read_from_pickle(result["key_filename"])
                return ElectronFileResponse(data=response)
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
            elif name == "stderr":
                response = handler.read_from_text(result["stderr_filename"])
                return ElectronFileResponse(data=response)
            elif name == "info":
                response = handler.read_from_text(result["info_filename"])
                return ElectronFileResponse(data=response)
            else:
                return ElectronFileResponse(data=None)
        else:
            return ElectronFileResponse(data=None)
