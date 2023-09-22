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
