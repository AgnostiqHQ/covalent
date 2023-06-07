# Copyright 2023 Agnostiq Inc.
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

"""
Types defining the runner-executor interface
"""

from enum import Enum
from typing import Dict, List

from pydantic import BaseModel

from covalent._shared_files.schemas.asset import AssetUpdate
from covalent._shared_files.util_classes import RESULT_STATUS


# Valid terminal statuses
class TerminalStatus(str, Enum):
    CANCELLED = RESULT_STATUS.CANCELLED
    COMPLETED = RESULT_STATUS.COMPLETED
    FAILED = RESULT_STATUS.FAILED


class TaskUpdate(BaseModel):
    dispatch_id: str
    node_id: int
    status: TerminalStatus
    assets: Dict[str, AssetUpdate]


class TaskSpec(BaseModel):
    function_id: int
    args_ids: List[int]
    kwargs_ids: Dict[str, int]
    deps_id: str
    call_before_id: str
    call_after_id: str


class ResourceMap(BaseModel):
    """Map resource identifiers to URIs"""

    # Map node_id to URI
    functions: Dict[int, str]

    # Map node_id to URI
    inputs: Dict[int, str]

    # Includes deps, call_before, call_after
    deps: Dict[str, str]
