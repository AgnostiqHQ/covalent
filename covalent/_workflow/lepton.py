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

from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from .._shared_files import logger
from .._shared_files.defaults import _DEFAULT_CONSTRAINT_VALUES
from .electron import Electron

if TYPE_CHECKING:
    from ..executor import BaseExecutor

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
        *,
        executor: Union[
            List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]
        ] = _DEFAULT_CONSTRAINT_VALUES["executor"],
    ) -> None:
        self.language = language
        self.library_name = library_name
        self.function_name = function_name
        # Types must be stored as strings, since not all type objects can be pickled
        self.argtypes = [(arg[0].__name__, arg[1]) for arg in argtypes]

        # Assign the wrapper below as the task's callable function
        super().__init__(self.wrap_task())

        # Assign metadata defaults
        super().set_metadata("executor", executor)

    def wrap_task(self) -> Callable:
        """Return a lepton wrapper function."""

        def python_wrapper(*args, **kwargs) -> Any:
            """Call a Python function specified in some other module."""

            import importlib

            try:
                module = importlib.import_module(self.library_name)
            except ModuleNotFoundError:
                app_log.warning(f"Could not import the module '{self.library_name}'.")
                raise

            try:
                func = getattr(module, self.function_name)
            except AttributeError:
                app_log.warning(
                    f"Could not find the function '{self.function_name}' in '{self.library_name}'."
                )
                raise

            # Foreign function invoked
            return func(*args, **kwargs)

        def c_wrapper(*args, **kwargs) -> Any:
            """Call a C function specified in a shared library."""

            import ctypes

            if kwargs:
                raise ValueError(
                    f"Keyword arguments {kwargs} are not supported when calling {self.function}."
                )

            try:
                handle = ctypes.CDLL(self.library_name)
            except OSError:
                app_log.warning(f"Could not open '{self.library_name}'.")
                raise

            # Format the variable type translation
            entrypoint = self.function_name
            types = []
            for t in self.argtypes:
                if t[0].startswith("LP_"):  # This is a pointer
                    types.append(ctypes.POINTER(getattr(ctypes, t[0][3:])))
                else:
                    types.append(getattr(ctypes, t[0]))
            attrs = [a[1] for a in self.argtypes]
            handle[entrypoint].argtypes = types
            handle[entrypoint].restype = None

            # Translate the variables
            c_func_args = []
            for idx, t in enumerate(types):
                arg = args[idx] if attrs[idx] != Lepton.OUTPUT else None

                # 1. The user specifies a scalar (non-subscriptable)
                #    and this variable returns data. It is transformed
                #    to a pointer and passed by address.
                if (
                    attrs[idx] != Lepton.INPUT
                    and not hasattr(arg, "__getitem__")
                    and types[idx].__name__.startswith("LP_")
                ):
                    if arg:
                        # The variable is used for input and output
                        c_func_args.append(ctypes.pointer(types[idx]._type_(arg)))
                    else:
                        # The variable is used for output only
                        c_func_args.append(ctypes.pointer(types[idx]._type_()))

                # 2. The user specifies an array (subscriptable)
                elif hasattr(arg, "__getitem__") and types[idx].__name__.startswith("LP_"):
                    c_func_args.append((types[idx]._type_ * len(arg))(*arg))

                # 3. Arg passed by value
                elif attrs[idx] == self.INPUT:
                    c_func_args.append(types[idx](arg))

                else:
                    raise ValueError("An invalid type was specified.")

            # Foreign function invoked
            handle[entrypoint](*c_func_args)

            # Format the return values
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
                    raise ValueError("An invalid return type was encountered.")

            if not return_vals:
                return None
            elif len(return_vals) == 1:
                return return_vals[0]
            else:
                return tuple(return_vals)

        if self.language in Lepton._LANG_PY:
            wrapper = python_wrapper
        elif self.language in Lepton._LANG_C:
            wrapper = c_wrapper
        else:
            raise ValueError(f"Language '{self.language}' is not supported.")

        # Attribute translation
        wrapper.__name__ = self.function_name
        wrapper.__qualname__ = f"Lepton.{self.library_name.split('.')[0]}.{self.function_name}"
        wrapper.__module__ += f".{self.library_name.split('.')[0]}"
        wrapper.__doc__ = (
            f"""Lepton interface for {self.language} function '{self.function_name}'."""
        )

        return wrapper
