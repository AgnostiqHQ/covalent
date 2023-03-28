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

"""FastAPI models for /api/v1/resultv2 endpoints"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..util_classes import Status
from .asset import AssetSchema

ELECTRON_METADATA_KEYS = {
    "task_group_id",
    "name",
    "start_time",
    "end_time",
    "status",
    # electron metadata
    "executor",
    "executor_data",
}

ELECTRON_ASSET_KEYS = {
    "function",
    "function_string",
    "output",
    "value",
    "error",
    "stdout",
    "stderr",
    # electron metadata
    "deps",
    "call_before",
    "call_after",
}


class ElectronAssets(BaseModel):
    function: AssetSchema
    function_string: AssetSchema
    value: AssetSchema
    output: AssetSchema
    error: Optional[AssetSchema]
    stdout: Optional[AssetSchema]
    stderr: Optional[AssetSchema]

    # electron_metadata
    deps: AssetSchema
    call_before: AssetSchema
    call_after: AssetSchema


class ElectronMetadata(BaseModel):
    task_group_id: int
    name: str
    executor: str
    executor_data: dict
    status: Optional[Status]
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class ElectronSchema(BaseModel):
    id: int
    metadata: ElectronMetadata
    assets: ElectronAssets
