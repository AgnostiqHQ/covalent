# Copyright 2023 Agnostiq Inc.
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

"""
Types defining the runner-executor interface
"""

from typing import Dict, List

from pydantic import BaseModel, field_validator

from covalent._shared_files.schemas.asset import AssetUpdate
from covalent._shared_files.util_classes import RESULT_STATUS, Status


class TaskUpdate(BaseModel):
    """Represents a task status update.

    Attributes:
        dispatch_id: The id of the dispatch.
        node_id: The id of the task.
        status: A Status dataclass representing the task's terminal status.
        assets: A map from asset keys to AssetUpdate objects
    """

    dispatch_id: str
    node_id: int
    status: Status
    assets: Dict[str, AssetUpdate]

    @field_validator("status")
    def validate_status(cls, v):
        if RESULT_STATUS.is_terminal(v):
            return v
        else:
            raise ValueError(f"Illegal status update {v}")


class TaskSpec(BaseModel):
    """An abstract description of a runnable task.

    Attributes:
        function_id: The `node_id` of the function.
        args_ids: The `node_id`s of the function's args
        kwargs_ids: The `node_id`s of the function's kwargs {key: node_id}
        deps_id: An opaque string representing the task's deps.
        call_before_id: An opaque string representing the task's call_before.
        call_after_id: An opaque string representing the task's call_before.

    The attribute values can be used in conjunction with a
    `ResourceMap` to locate the actual resources in the compute
    environment.
    """

    function_id: int
    args_ids: List[int]
    kwargs_ids: Dict[str, int]
    deps_id: str
    call_before_id: str
    call_after_id: str


class ResourceMap(BaseModel):

    """Map resource identifiers to URIs.

    The resources may be loaded in the compute environment from these
    URIs.

    Resource identifiers are the attribute values of TaskSpecs. For
    instance, if ts is a `TaskSpec` and rm is the corresponding
    `ResourceMap`, then
    - the serialized function has URI `rm.functions[ts.function_id]`
    - the serialized args have URIs `rm.inputs[ts.args_ids[i]]`
    - the call_before has URI `rm.deps[ts.call_before_id]`

    Attributes:
        functions: A map from node id to the corresponding URI.
        inputs: A map from node id to the corresponding URI
        deps: A map from deps resource ids to their corresponding URIs.

    """

    # Map node_id to URI
    functions: Dict[int, str]

    # Map node_id to URI
    inputs: Dict[int, str]

    # Includes deps, call_before, call_after
    deps: Dict[str, str]


class TaskGroup(BaseModel):
    """Description of a group of runnable graph nodes.

    Attributes:
        dispatch_id: The `dispatch_id`.
        task_ids: The graph nodes comprising the task group.
        task_group_id: The task group identifier.
    """

    dispatch_id: str
    task_ids: List[int]
    task_group_id: int
