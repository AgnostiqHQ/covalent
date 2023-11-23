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

"""Request and response models for Electrons"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Union

from pydantic import BaseModel

from covalent_ui.api.v1.utils.status import Status


class Job(BaseModel):
    job_id: Union[str, None] = None
    start_time: Union[datetime, None] = None
    executor: Union[str, None] = None
    status: Union[str, None] = None


class JobsResponse(BaseModel):
    data: Union[List[Job], None] = None
    msg: Union[str, None] = None


class JobDetails(BaseModel):
    overview: Union[dict, None] = None
    circuit: Union[dict, None] = None
    executor: Union[dict, None] = None


class JobDetailsResponse(BaseModel):
    data: Union[JobDetails, None, Dict] = None
    msg: Union[str, None] = None


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
    runtime: Union[int, float, None] = None
    description: Union[str, None] = None
    qelectron_data_exists: bool = False
    qelectron: Union[dict, None] = None


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
