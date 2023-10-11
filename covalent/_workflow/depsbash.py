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
from copy import deepcopy
from typing import List, Union

from .deps import Deps
from .transport import TransportableObject


def apply_bash_commands(commands):
    for cmd in commands:
        subprocess.run(
            cmd, stdin=subprocess.DEVNULL, shell=True, capture_output=True, check=True, text=True
        )


class DepsBash(Deps):
    """Shell commands to run before an electron

    Deps class to encapsulate Bash dependencies for an electron.

    The specified commands will be executed as subprocesses in the
    same environment as the electron.

    Attributes:
        commands: A list of bash commands to execute before the electron runs.

    """

    def __init__(self, commands: Union[List, str] = []):
        if isinstance(commands, str):
            self.commands = [commands]
        else:
            self.commands = commands

        super().__init__(apply_fn=apply_bash_commands, apply_args=[self.commands])

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        attributes = self.__dict__.copy()
        for k, v in attributes.items():
            if isinstance(v, TransportableObject):
                attributes[k] = v.to_dict()
        return {"type": "DepsBash", "short_name": self.short_name(), "attributes": attributes}

    def from_dict(self, object_dict) -> "DepsBash":
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
