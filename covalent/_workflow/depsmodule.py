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
from types import ModuleType
from typing import Union

from .depscall import DepsCall
from .transportable_object import TransportableObject


class DepsModule(DepsCall):
    """
    Python modules to be imported in an electron's execution environment.

    This is only used as a vehicle to send the module by reference to the
    to the right place of serialization where it will instead be pickled by value.

    Deps class to encapsulate python modules to be
    imported in the same execution environment as the electron.

    Note: This subclasses the DepsCall class due to its pre-existing
    infrastructure integrations, and not because of its logical functionality.

    Attributes:
        module_name: A string containing the name of the module to be imported.
    """

    def __init__(self, module: Union[str, ModuleType]):
        if isinstance(module, str):
            # Import the module on the client side
            module = importlib.import_module(module)

        # Temporarily pickling the module by reference
        # so that it can be pickled by value when serializing
        # the transport graph.
        self.pickled_module = TransportableObject(module)

        super().__init__()

    def short_name(self):
        """Returns the short name of this class."""
        return "depsmodule"
