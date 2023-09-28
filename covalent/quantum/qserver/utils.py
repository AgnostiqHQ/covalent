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

import datetime
import importlib
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import orjson
from pydantic import BaseModel

from ..._shared_files.qinfo import QNodeSpecs
from ...executor.qbase import BaseQExecutor

BATCH_ID_SEPARATOR = "@"
MAX_DIFFERENT_EXECUTORS = 10


class CircuitInfo(BaseModel):
    electron_node_id: Optional[int] = None
    dispatch_id: Optional[str] = None
    circuit_name: Optional[str] = None
    circuit_description: Optional[str] = None
    circuit_diagram: Optional[str] = None
    qnode_specs: Optional[Union[Dict[str, Any], QNodeSpecs]] = None
    qexecutor: Optional[BaseQExecutor] = None
    save_time: datetime.datetime
    circuit_id: Optional[str] = None
    qscript: Optional[str] = None
    execution_time: Optional[float] = None
    result: Optional[List[Any]] = None
    result_metadata: Optional[List[Dict[str, Any]]] = None


@lru_cache
def get_cached_module():
    return importlib.import_module(".executor", package="covalent")


def executor_from_dict(executor_dict: Dict):
    if "executors" in executor_dict:
        executors = [executor_from_dict(ed) for ed in executor_dict["executors"]]
        executor_dict["executors"] = executors

    name = executor_dict["name"]
    executor_class = getattr(get_cached_module(), name)
    return executor_class(**executor_dict)


@lru_cache(maxsize=MAX_DIFFERENT_EXECUTORS)
def get_cached_executor(**executor_dict):
    if "executors" in executor_dict:
        executors = tuple(orjson.loads(ex) for ex in executor_dict["executors"])
        executor_dict["executors"] = executors

    return executor_from_dict(executor_dict)


def reconstruct_executors(deconstructed_executors: List[Dict]):
    return [executor_from_dict(de) for de in deconstructed_executors]


def get_circuit_id(batch_id, circuit_number):
    return f"circuit_{circuit_number}{BATCH_ID_SEPARATOR}{batch_id}"
