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
from typing import Any, Dict, List

import orjson
from pydantic import BaseModel

from ...executor.qbase import BaseQExecutor

BATCH_ID_SEPARATOR = "@"
MAX_DIFFERENT_EXECUTORS = 10


class CircuitInfo(BaseModel):
    electron_node_id: str = None
    dispatch_id: str = None
    circuit_name: str = None
    circuit_description: str = None
    circuit_diagram: str = None
    qnode_specs: Dict[str, Any] = None
    qexecutor: BaseQExecutor = None
    save_time: datetime.datetime
    circuit_id: str = None
    qscript: str = None
    execution_time: float = None
    result: List[Any] = None
    result_metadata: List[Dict[str, Any]] = None


def reconstruct_executors(deconstructed_executors: List[Dict]):
    return [executor_from_dict(de) for de in deconstructed_executors]


def get_circuit_id(batch_id, circuit_number):
    return f"circuit_{circuit_number}{BATCH_ID_SEPARATOR}{batch_id}"
