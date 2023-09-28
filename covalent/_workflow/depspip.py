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

import subprocess
import tempfile
from copy import deepcopy
from typing import List, Union

from .deps import Deps
from .transport import TransportableObject


def apply_pip_deps(pkgs: [] = [], requirements_content: str = ""):
    if requirements_content:
        reqs_filename = ""
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(requirements_content)
            reqs_filename = f.name
        cmd = f"pip install --no-input -r {reqs_filename}".split()

    else:
        pkg_list = " ".join(pkgs)
        cmd = f"pip install --no-input {pkg_list}".split()

    subprocess.run(cmd, stdin=subprocess.DEVNULL, check=True, capture_output=True)


class DepsPip(Deps):
    """PyPI packages to be installed before executing an electron

    A specification of Pip packages to be installed

    Attributes:
        packages: A list of PyPI packages to install
        reqs_path: Path to requirements.txt (overrides `packages`)

    These packages are installed in an electron's execution
    environment just before the electron is run.

    """

    def __init__(self, packages: Union[List, str] = [], reqs_path: str = ""):
        if isinstance(packages, str):
            self.packages = [packages]
        else:
            self.packages = packages

        self.reqs_path = reqs_path
        self.requirements_content = ""

        if self.reqs_path:
            with open(self.reqs_path, "r") as f:
                self.requirements_content = f.read()

        apply_args = [self.packages, self.requirements_content]

        super().__init__(apply_fn=apply_pip_deps, apply_args=apply_args)

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        attributes = self.__dict__.copy()
        for k, v in attributes.items():
            if isinstance(v, TransportableObject):
                attributes[k] = v.to_dict()
        return {"type": "DepsPip", "short_name": self.short_name(), "attributes": attributes}

    def from_dict(self, object_dict) -> "DepsPip":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            self

        Instance attributes will be overwritten.
        """

        if not object_dict:
            return self

        attributes = deepcopy(object_dict)["attributes"]
        for k, v in attributes.items():
            if isinstance(v, dict) and v.get("type", None) == "TransportableObject":
                attributes[k] = TransportableObject.from_dict(v)

        self.__dict__ = attributes

        return self
