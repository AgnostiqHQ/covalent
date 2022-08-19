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

from enum import Enum

from pydantic import BaseModel

from covalent_ui.api.v1.utils.status import Status


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


class FileOutput(str, Enum):
    FUNCTION_STRING = "function_string"
    FUNCTION = "function"
    EXECUTOR = "executor"
    RESULT = "result"
    VALUE = "value"
    KEY = "key"
    STDOUT = "stdout"
    DEPS = "deps"
    CALL_BEFORE = "call_before"
    CALL_AFTER = "call_after"
    ERROR = "error"
    INFO = "info"
    INPUTS = "inputs"
