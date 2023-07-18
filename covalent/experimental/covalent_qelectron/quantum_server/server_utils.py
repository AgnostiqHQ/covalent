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

from ..executors.base import BaseQExecutor

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


@lru_cache
def get_cached_module():
    return importlib.import_module(
        ".experimental.covalent_qelectron.quantum_server.proxy_executors",
        package="covalent"
    )


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


def make_selector_args_hashable(selected_executor_dict: dict):
    # the selected_executor_dict cannot contain unhashable types like dicts.
    # This can happen if **kwargs was passed at any point. We must collapse this dict
    keys_to_remove = []  # To store keys that need to be removed after merging nested dictionaries

    for key, value in selected_executor_dict.items():
        if isinstance(value, dict):
            selected_executor_dict.update(value)
            keys_to_remove.append(key)

    # Remove the keys that were merged from nested dictionaries
    for key in keys_to_remove:
        selected_executor_dict.pop(key)
    return selected_executor_dict
