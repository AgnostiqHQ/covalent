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


@routes.get("/electron/{electron_id}/", response_model=ElectronResponse)
def get_electron_details(electron_id: uuid.UUID):
    """Get Electron Details

    Args:
        electron_id: To fetch electron data with the provided electron id.

    Returns:
        Returns the electron details
    """
    response = graph_data()["items"]
    for results in response:
        for data in results["graph"]["nodes"]:
            if data["electron_id"] == str(electron_id):
                return ElectronResponse(item=data)
    return ElectronResponse(item=None)


@routes.get("/electron/{electron_id}/get-file/{file_module}", response_model=ElectronErrorResponse)
def get_electron_file(electron_id: uuid.UUID, file_module: FileOutput):
    """Get Electron File

    Args:
        electron_id: To fetch electron data with the provided electron id.
        file_module: The type of file that needs to be fetched

    Returns:
        Returns the content of the file with the parameters provided
    """
    response = graph_data()["items"]
    for results in response:
        for data in results["graph"]["nodes"]:
            if data["electron_id"] == str(electron_id):
                return ElectronErrorResponse(file=str(data[file_module]))
    return ElectronErrorResponse(file=None)
