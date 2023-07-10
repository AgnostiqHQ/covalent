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

import importlib
import inspect
from typing import Any, Tuple

import cloudpickle


_IMPORT_PATH_SEPARATOR = ":"


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
    module = inspect.getmodule(obj)
    if module:
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
