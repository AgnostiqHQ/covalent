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

"""Request and response models for Electrons"""

from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel

from covalent_ui.api.v1.utils.status import Status


class ElectronResponse(BaseModel):
    """Electron Response Model"""

    id: Union[int, None] = None
    node_id: Union[int, None] = None
    parent_lattice_id: Union[int, None] = None
    type: Union[str, None] = None
    storage_path: Union[str, None] = None
    name: Union[str, None] = None
    status: Union[str, None] = None
    started_at: Union[datetime, None] = None
    ended_at: Union[datetime, None] = None
    runtime: Union[int, None] = None
    description: Union[str, None] = None


class ElectronFileResponse(BaseModel):
    """Electron Response Model"""

    data: Union[str, None] = None
    python_object: Union[str, None] = None


class ElectronExecutorResponse(BaseModel):
    """Electron File Response Model"""

    executor_name: Union[str, None] = None
    executor_details: Union[dict, None] = None


class ElectronErrorResponse(BaseModel):
    """Electron Error Response Model"""

    data: Union[str, None] = None


class ElectronFunctionResponse(BaseModel):
    """Electron Function Response Model"""

    data: Union[str, None] = None


class ElectronResponseModel(BaseModel):
    """Electron Response Validation"""

    id: int
    parent_lattice_id: int
    transport_graph_node_id: int
    type: str
    name: str
    status: Status
    executor: str
    created_at: str
    started_at: str
    completed_at: str
    updated_at: str


class ElectronFileOutput(str, Enum):
    """Electron file output"""

    FUNCTION_STRING = "function_string"
    FUNCTION = "function"
    EXECUTOR = "executor"
    RESULT = "result"
    VALUE = "value"
    STDOUT = "stdout"
    DEPS = "deps"
    CALL_BEFORE = "call_before"
    CALL_AFTER = "call_after"
    ERROR = "error"
    INFO = "info"
    INPUTS = "inputs"
