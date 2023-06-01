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

from .asset import AssetSchema
from .common import StatusEnum

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

ELECTRON_FUNCTION_FILENAME = "function.tobj"
ELECTRON_FUNCTION_STRING_FILENAME = "function_string.txt"
ELECTRON_VALUE_FILENAME = "value.tobj"
ELECTRON_STDOUT_FILENAME = "stdout.log"
ELECTRON_STDERR_FILENAME = "stderr.log"
ELECTRON_ERROR_FILENAME = "error.log"
ELECTRON_RESULTS_FILENAME = "results.tobj"
ELECTRON_DEPS_FILENAME = "deps.json"
ELECTRON_CALL_BEFORE_FILENAME = "call_before.json"
ELECTRON_CALL_AFTER_FILENAME = "call_after.json"
ELECTRON_STORAGE_TYPE = "file"


ASSET_FILENAME_MAP = {
    "function": ELECTRON_FUNCTION_FILENAME,
    "function_string": ELECTRON_FUNCTION_STRING_FILENAME,
    "value": ELECTRON_VALUE_FILENAME,
    "output": ELECTRON_RESULTS_FILENAME,
    "deps": ELECTRON_DEPS_FILENAME,
    "call_before": ELECTRON_CALL_BEFORE_FILENAME,
    "call_after": ELECTRON_CALL_AFTER_FILENAME,
    "stdout": ELECTRON_STDOUT_FILENAME,
    "stderr": ELECTRON_STDERR_FILENAME,
    "error": ELECTRON_ERROR_FILENAME,
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
    sub_dispatch_id: Optional[str]
    status: StatusEnum
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    # For use by redispatch
    def reset(self):
        self.status = StatusEnum.NEW_OBJECT
        self.start_time = None
        self.end_time = None


class ElectronSchema(BaseModel):
    id: int
    metadata: ElectronMetadata
    assets: ElectronAssets
