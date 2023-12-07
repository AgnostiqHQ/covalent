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

import cloudpickle as pickle

from .depscall import DepsCall


def _client_side_pickle_module(module: Union[str, ModuleType]):
    """
    Pickle a module by value on the client side
    and return the pickled bytes.

    Args:
        module: The name of the module to pickle, can also be a module.
                     This module must be importable on the client side.

    Returns:
        The pickled bytes of the module.
    """

    if isinstance(module, str):
        # Import the module on the client side
        module = importlib.import_module(module)

    # Register the module with cloudpickle by value
    pickle.register_pickle_by_value(module)

    # Pickle the module
    pickled_module = pickle.dumps(module)

    # Unregister the module with cloudpickle
    pickle.unregister_pickle_by_value(module)

    return pickled_module


def _server_side_import_module(module_name: str, module_pickle: bytes):
    """
    Import a module by value on the server side
    from a pickled module.

    Args:
        module_name: The name of the module to import.
        module_pickle: The pickled bytes of the module.

    Returns:
        The imported module.
    """

    import importlib
    import sys

    pkg_name = module_name.split(".")[0]
    rel_module_name = module_name[len(pkg_name) + 1 :]

    # Unpickle the module
    module = pickle.loads(module_pickle)

    # Add the module to the server side's sys.modules
    sys.modules[module_name] = module

    importlib.import_module(rel_module_name, package=pkg_name)


class DepsModule(DepsCall):
    """
    Python modules to be imported in an electron's execution environment

    Deps class to encapsulate python modules to be
    imported in the same execution environment as the electron.

    Attributes:
        module_name: A string containing the name of the module to be imported.
    """

    def __init__(self, module: Union[str, ModuleType]):
        module_name = module if isinstance(module, str) else module.__name__

        print("module_name:", module_name)

        # Pickle the module by value on the client side
        module_pickle = _client_side_pickle_module(module)

        # Pass the pickled module to the server side
        func = _server_side_import_module
        args = [module_name, module_pickle]
        kwargs = {}

        super().__init__(func, args, kwargs)
