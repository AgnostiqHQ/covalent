# Copyright 2021 Agnostiq Inc.
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

import sys
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import Callable, Dict, List, Union

from .deps import Deps
from .transport import TransportableObject

_MODULES_DIRNAME = "/tmp/covalent_depslocal"  # TODO: make parameter


def local_deps(func) -> Callable:
    """Add local modules directory to the system path"""

    @wraps(func)
    def _func(*args, **kwargs):
        modules_path = str(Path(_MODULES_DIRNAME).resolve())
        if modules_path not in sys.path[:2]:
            sys.path.insert(1, modules_path)
        return func(*args, **kwargs)

    return _func


def create_modules(modules: Dict[str, str]) -> None:
    """Write module files in the execution environment"""
    modules_dir = Path(_MODULES_DIRNAME).resolve()
    modules_dir.mkdir(exist_ok=True)

    for name, text in modules.items():
        with open(modules_dir / name, "w", encoding="utf8") as module_file:
            module_file.write(text)


class DepsLocal(Deps):
    """Local Python modules required to run an electron

    Deps class to encapsulate module dependencies for an electron.

    The specified modules will be created in the remote execution environment.

    Attributes:
        modules: A dictionary of filename-text pairs representing each module.

    """

    def __init__(self,
                 modules: Union[str, List[str]] = None,
                 path: Union[str, Path] = None):

        if isinstance(modules, str):
            modules = [modules]

        if isinstance(path, str):
            path = Path(path).resolve()
        elif path is None:
            path = Path(".").resolve()

        self.module_content = {}

        for module_name in modules or []:
            module_path = DepsLocal.check_module(path, module_name)
            with open(module_path, "r", encoding="utf8") as module_file:
                self.module_content[module_path.name] = "".join(module_file.readlines())

        super().__init__(apply_fn=create_modules, apply_args=[self.module_content])

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        attributes = self.__dict__.copy()
        for k, v in attributes.items():
            if isinstance(v, TransportableObject):
                attributes[k] = v.to_dict()
            else:
                attributes[k] = v
        return {
            "type": self.__class__.__name__,
            "short_name": self.short_name(),
            "attributes": attributes,
        }

    def from_dict(self, object_dict) -> "DepsLocal":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            self

        Instance attributes will be overwritten.
        """
        if not object_dict:
            return self

        attributes = deepcopy(object_dict["attributes"])
        for k, v in attributes.items():
            if isinstance(v, dict) and v.get("type") == "TransportableObject":
                attributes[k] = TransportableObject.from_dict(v)
        self.__dict__ = attributes
        return self

    def short_name(self) -> str:
        """A comma-separated string of local Python modules"""
        return f"({', '.join(list(self.module_content))})"

    @staticmethod
    def check_module(location: Path, module_name: str) -> Path:
        """Get the absolute path to a local Python module specified as
        'module' or 'module.py'.
        """
        module_path = location / module_name

        if not module_path.name.endswith(".py"):
            module_path = module_path.parent / f"{module_path.name}.py"

        if not module_path.exists():
            raise FileNotFoundError(f"Python module '{module_path}' does not exist.")

        return module_path
