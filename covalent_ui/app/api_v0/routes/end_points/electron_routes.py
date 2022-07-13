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

from fastapi import APIRouter
from httplib2 import Response
from sqlalchemy.orm import Session

from covalent_ui.app.api_v0.data_layer.electron_dal import Electrons
from covalent_ui.app.api_v0.database.config.db import engine
from covalent_ui.app.api_v0.database.graph_data import graph_data
from covalent_ui.app.api_v0.models.lattices_model import ElectronErrorResponse, ElectronResponse

routes: APIRouter = APIRouter()


class FileOutput(str, Enum):
    """File Output

    Attributes:
        FUNCTION_STRING: Function String File
        ERROR: Error File
    """

    FUNCTION_STRING = "function_string"
    ERROR = "error"


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
            return ElectronResponse(item=None)
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
