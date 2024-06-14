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

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from covalent._shared_files.schemas.result import StatusEnum

range_regex = "bytes=([0-9]+)-([0-9]*)"
range_pattern = re.compile(range_regex)

digest_regex = "(sha|sha-256)=([0-9a-f]+)"
digest_pattern = re.compile(digest_regex)


class DispatchAssetKey(str, Enum):
    result = "result"
    error = "error"


class LatticeAssetKey(str, Enum):
    workflow_function = "workflow_function"
    workflow_function_string = "workflow_function_string"
    doc = "doc"
    inputs = "inputs"
    hooks = "hooks"


class ElectronAssetKey(str, Enum):
    function = "function"
    function_string = "function_string"
    output = "output"
    value = "value"
    hooks = "hooks"
    error = "error"
    stdout = "stdout"
    stderr = "stderr"
    qelectron_db = "qelectron_db"


class AssetRepresentation(str, Enum):
    string = "string"
    b64pickle = "object"


class TargetDispatchStatus(str, Enum):
    running = "RUNNING"
    cancelled = "CANCELLED"


class DispatchStatusSetSchema(BaseModel):
    # The target status
    status: TargetDispatchStatus

    # For cancellation, an optional list of task ids to cancel
    task_ids: Optional[List] = []


class BulkGetMetadata(BaseModel):
    count: int


class DispatchSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dispatch_id: str
    root_dispatch_id: Optional[str] = None
    status: StatusEnum
    name: Optional[str] = None
    electron_num: Optional[int] = None
    completed_electron_num: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class BulkDispatchGetSchema(BaseModel):
    dispatches: List[DispatchSummary]
    metadata: BulkGetMetadata
