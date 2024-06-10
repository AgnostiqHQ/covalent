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

import importlib
import inspect
from typing import Any, Tuple

import cloudpickle
from pennylane._device import Device

from .logger import app_log
from .pickling import _qml_mods_pickle

_IMPORT_PATH_SEPARATOR = ":"


def get_qelectron_db_path(dispatch_id: str, task_id: int):
    """
    Return the path to the Qelectron database for a given dispatch_id and task_id.

    WARNING: SHOULD ONLY BE USED FROM THE SAME MACHINE
    AS WHERE THE USER'S TASK FUNCTION IS BEING RUN.
    """

    from covalent.quantum.qserver.database import Database

    database = Database()

    db_path = database.get_db_path(dispatch_id=dispatch_id, node_id=task_id)

    if db_path.exists():
        app_log.debug(f"Found qelectron DB for task {task_id}")
        return db_path
    else:
        app_log.debug(f"Qelectron database not found for task {task_id}")
        return None


@_qml_mods_pickle
def cloudpickle_serialize(obj):
    return cloudpickle.dumps(obj)


def cloudpickle_deserialize(obj):
    return cloudpickle.loads(obj)


def select_first_executor(qnode, executors):
    """Selects the first executor to run the qnode"""
    return executors[0]


def get_import_path(obj) -> Tuple[str, str]:
    """
    Determine the import path of an object.
    """
    if module := inspect.getmodule(obj):
        module_path = module.__name__
        class_name = obj.__name__
        return f"{module_path}{_IMPORT_PATH_SEPARATOR}{class_name}"
    raise RuntimeError(f"Unable to determine import path for {obj}.")


def import_from_path(path: str) -> Any:
    """
    Import a class from a path.
    """
    module_path, class_name = path.split(_IMPORT_PATH_SEPARATOR)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_original_shots(dev: Device):
    """
    Recreate vector of shots if device has a shot vector.
    """
    if not dev.shot_vector:
        return dev.shots

    shot_sequence = []
    for shots in dev.shot_vector:
        shot_sequence.extend([shots.shots] * shots.copies)
    return type(dev.shot_vector)(shot_sequence)
