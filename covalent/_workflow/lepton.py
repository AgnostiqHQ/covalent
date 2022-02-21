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

"""Language translation module for Electron objects."""

from typing import Any, Callable, List, Optional

from .._shared_files import logger
from .electron import Electron

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class Lepton(Electron):
    """
    A generalization of an Electron to languages other than Python.

    Leptons inherit from Electrons, overloading the `function` attribute
    with a wrapper function. Users specify the foreign function's signature
    as well as its location by providing a library and entrypoint. When one
    of the executors invokes the task's `function`, the foreign function
    is called by way of the wrapper function defined here. If compilation
    scripts are required, these must be separately copied to the backend.

    Attributes:
        language: Language in which the task specification is written.
        library_name: Name of the library or module which specifies the function.
        function_name: Name of the foreign function.
        argtypes: List of tuples specifying data types and input/output properties.
    """

    INPUT = 0
    OUTPUT = 1
    INPUT_OUTPUT = 2

    _LANG_PY = ["Python", "python"]
    _LANG_C = ["C", "c"]

    def __init__(
        self,
        language: str = "python",
        library_name: str = "",
        function_name: str = "",
        argtypes: Optional[List] = [],
    ) -> None:
        self.language = language
        self.library_name = library_name
        self.function_name = function_name
        self.argtypes = argtypes

        # Assign the wrapper below as the task's callable function
        super().__init__(self.wrap_task())

    def wrap_task(self) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Call a Python function specified in some other module
            if self.language in Lepton._LANG_PY:
                import importlib

                try:
                    module = importlib.import_module(self.library_name)
                except ModuleNotFoundError:
                    app_log.warning(f"Could not import the module '{self.library_name}'.")
                    return

                try:
                    func = getattr(module, self.function_name)
                except AttributeError:
                    app_log.warning(
                        f"Could not find the function '{self.function_name}' in '{self.library_name}'."
                    )
                    return

                # Foreign function invoked
                return func(*args, **kwargs)

            # Call a C function specified in a shared library
            elif self.language in Lepton._LANG_C:
                from ctypes import CDLL, pointer

                if kwargs:
                    app_log.warning(
                        f"Keyword arguments are not supported when calling {self.function}."
                    )
                    return

                try:
                    handle = CDLL(self.library_name)
                except OSError:
                    app_log.warning(f"Could not open '{self.library_name}'.")
                    return

                entrypoint = self.function_name
                types = [t[0] for t in self.argtypes]
                attrs = [a[1] for a in self.argtypes]
                handle[entrypoint].argtypes = types
                handle[entrypoint].restype = None

                c_func_args = []
                for idx, (t, arg) in enumerate(zip(types, args)):
                    # 1. The user specifies a scalar (non-subscriptable)
                    #    and this variable returns data. It is transformed
                    #    to a pointer and passed by address.
                    if (
                        attrs[idx] != Lepton.INPUT
                        and not hasattr(arg, "__getitem__")
                        and types[idx].__name__.startswith("LP_")
                    ):
                        c_func_args.append(pointer(types[idx]._type_(arg)))

                    # 2. The user specifies an array (subscriptable)
                    elif hasattr(arg, "__getitem__") and types[idx].__name__.startswith("LP_"):
                        c_func_args.append((types[idx]._type_ * len(arg))(*arg))

                    # 3. Arg passed by value
                    elif attrs[idx] == self.INPUT:
                        c_func_args.append(types[idx]._type_(arg))

                    else:
                        app_log.warning("An invalid type was specified.")
                        return

                # Foreign function invoked
                handle[entrypoint](*c_func_args)

                # Format return values
                return_vals = []
                for idx, arg in enumerate(c_func_args):
                    if attrs[idx] == self.INPUT:
                        continue

                    # 1. Convert pointers to scalars
                    if hasattr(arg, "contents"):
                        return_vals.append(arg.contents.value)

                    # 2. This is a subscriptable object
                    elif hasattr(arg, "__getitem__"):
                        return_vals.append([x.value for x in arg])

                    # If we end up here, the previous if/else block needs improving
                    else:
                        app_log.error("An invalid return type was encountered.")
                        return

                if not return_vals:
                    return None
                elif len(return_vals) == 1:
                    return return_vals[0]
                else:
                    return tuple(return_vals)

            else:
                app_log.warning(f"Language '{self.language}' is not supported.")
                return

        return wrapper
