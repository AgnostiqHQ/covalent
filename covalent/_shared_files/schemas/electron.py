# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI models for /api/v1/resultv2 endpoints"""

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from .asset import AssetSchema
from .common import StatusEnum

ELECTRON_METADATA_KEYS = {
    "task_group_id",
    "name",
    "start_time",
    "end_time",
    "status",
    # user dependent metadata
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
    # user dependent assets
    "hooks",
}

ELECTRON_FUNCTION_FILENAME = "function.tobj"
ELECTRON_FUNCTION_STRING_FILENAME = "function_string.txt"
ELECTRON_VALUE_FILENAME = "value.tobj"
ELECTRON_STDOUT_FILENAME = "stdout.log"
ELECTRON_STDERR_FILENAME = "stderr.log"
ELECTRON_ERROR_FILENAME = "error.log"
ELECTRON_RESULTS_FILENAME = "results.tobj"
ELECTRON_HOOKS_FILENAME = "hooks.json"
ELECTRON_CALL_BEFORE_FILENAME = "call_before.json"
ELECTRON_CALL_AFTER_FILENAME = "call_after.json"
ELECTRON_STORAGE_TYPE = "file"


ASSET_FILENAME_MAP = {
    "function": ELECTRON_FUNCTION_FILENAME,
    "function_string": ELECTRON_FUNCTION_STRING_FILENAME,
    "value": ELECTRON_VALUE_FILENAME,
    "output": ELECTRON_RESULTS_FILENAME,
    "stdout": ELECTRON_STDOUT_FILENAME,
    "stderr": ELECTRON_STDERR_FILENAME,
    "error": ELECTRON_ERROR_FILENAME,
    "hooks": ELECTRON_HOOKS_FILENAME,
}


class ElectronAssets(BaseModel):
    function: AssetSchema
    function_string: AssetSchema
    value: AssetSchema
    output: AssetSchema
    error: Optional[AssetSchema] = None
    stdout: Optional[AssetSchema] = None
    stderr: Optional[AssetSchema] = None

    # user dependent assets
    hooks: AssetSchema

    _custom: Optional[Dict[str, AssetSchema]] = None


class ElectronMetadata(BaseModel):
    task_group_id: int
    name: str
    executor: str
    executor_data: dict
    sub_dispatch_id: Optional[str] = None
    status: StatusEnum
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    _custom: Optional[Dict] = None

    # For use by redispatch
    def reset(self):
        self.status = StatusEnum.NEW_OBJECT
        self.start_time = None
        self.end_time = None


class ElectronSchema(BaseModel):
    id: int
    metadata: ElectronMetadata
    assets: ElectronAssets
