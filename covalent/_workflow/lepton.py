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

from builtins import list
from dataclasses import asdict
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Union

from .._file_transfer.enums import Order
from .._file_transfer.file_transfer import FileTransfer
from .._shared_files import logger
from .._shared_files.defaults import DefaultMetadataValues
from .depsbash import DepsBash
from .depscall import RESERVED_RETVAL_KEY__FILES, DepsCall
from .depspip import DepsPip
from .electron import Electron
from .transport import encode_metadata

if TYPE_CHECKING:  # pragma: no cover
    from ..executor import BaseExecutor

DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())

app_log = logger.app_log
log_stack_info = logger.log_stack_info

# TODO: Review exceptions/errors


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
        executor: Alternative executor object to be used for lepton execution. If not passed, the dask
        executor is used by default
        files: An optional list of FileTransfer objects which copy files to/from remote or local filesystems.
    """

    INPUT = 0
    OUTPUT = 1
    INPUT_OUTPUT = 2

    _LANG_PY = ["Python", "python"]
    _LANG_C = ["C", "c"]
    _LANG_SHELL = ["bash", "shell"]
    _SCRIPTING_LANGUAGES = _LANG_PY + _LANG_SHELL

    def __init__(
        self,
        language: str = "python",
        *,
        library_name: str = "",
        function_name: str = "",
        argtypes: Optional[List] = [],
        command: Optional[Union[str, List[str]]] = "",
        named_outputs: Optional[List[str]] = [],
        display_name: Optional[str] = "",
        executor: Union[
            List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]
        ] = DEFAULT_METADATA_VALUES["executor"],
        files: List[FileTransfer] = [],
        deps_bash: Union[DepsBash, List, str] = DEFAULT_METADATA_VALUES["deps"].get("bash", []),
        deps_pip: Union[DepsPip, list] = DEFAULT_METADATA_VALUES["deps"].get("pip", None),
        call_before: Union[List[DepsCall], DepsCall] = DEFAULT_METADATA_VALUES["call_before"],
        call_after: Union[List[DepsCall], DepsCall] = DEFAULT_METADATA_VALUES["call_after"],
    ) -> None:
        self.language = language
        self.library_name = library_name
        self.function_name = function_name
        # Types must be stored as strings, since not all type objects can be pickled
        self.argtypes = [(arg[0].__name__, arg[1]) for arg in argtypes]
        self.command = command
        self.named_outputs = named_outputs
        self.display_name = display_name

        if self.language in Lepton._SCRIPTING_LANGUAGES:
            if self.command and self.library_name:
                raise ValueError(
                    "Invalid argument combination: library_name and command. Use one or the other."
                )

            if not (self.command or self.library_name):
                raise ValueError("Specify either library_name or command using this language.")
        else:
            if command:
                raise ValueError(
                    f"Keyword argument 'command' incompatible with language {self.language}."
                )
            if named_outputs:
                raise ValueError(
                    f"Keyword argument 'named_outputs' incompatible with language {self.language}."
                )

        if self.library_name and not self.function_name:
            raise ValueError("Must specify function_name when calling a library.")

        # Syncing behavior of file transfer with an electron
        internal_call_before_deps = []
        internal_call_after_deps = []

        for file_transfer in files:
            _file_transfer_pre_hook_, _file_transfer_call_dep_ = file_transfer.cp()

            # pre-file transfer hook to create any necessary temporary files
            internal_call_before_deps.append(
                DepsCall(
                    _file_transfer_pre_hook_,
                    retval_keyword=RESERVED_RETVAL_KEY__FILES,
                    override_reserved_retval_keys=True,
                )
            )

            if file_transfer.order == Order.AFTER:
                internal_call_after_deps.append(DepsCall(_file_transfer_call_dep_))
            else:
                internal_call_before_deps.append(DepsCall(_file_transfer_call_dep_))

        # Copied from electron.py
        deps = {}

        if isinstance(deps_bash, DepsBash):
            deps["bash"] = deps_bash
        if isinstance(deps_bash, list) or isinstance(deps_bash, str):
            deps["bash"] = DepsBash(commands=deps_bash)

        if isinstance(deps_pip, DepsPip):
            deps["pip"] = deps_pip
        if isinstance(deps_pip, list):
            deps["pip"] = DepsPip(packages=deps_pip)

        if isinstance(call_before, DepsCall):
            call_before = [call_before]

        if isinstance(call_after, DepsCall):
            call_after = [call_after]

        call_before = internal_call_before_deps + call_before
        call_after = internal_call_after_deps + call_after

        # Leptons do not currently support retval_keyword(s) from DepsCall
        for cd in call_after + call_before:
            return_value_keyword = cd.retval_keyword
            if return_value_keyword in [RESERVED_RETVAL_KEY__FILES]:
                cd.retval_keyword = None
            elif return_value_keyword:
                raise Exception(
                    "DepsCall retval_keyword(s) are not currently supported for Leptons, please remove the retval_keyword arg from DepsCall for the workflow to be constructed successfully."
                )

        # Should be synced with electron
        constraints = {
            "executor": executor,
            "deps": deps,
            "call_before": call_before,
            "call_after": call_after,
        }

        constraints = encode_metadata(constraints)

        # Assign the wrapper below as the task's callable function
        super().__init__(self.wrap_task())

        # Assign metadata
        for k, v in constraints.items():
            super().set_metadata(k, v)

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

        def shell_wrapper(*args, **kwargs) -> Any:
            """Invoke a shell function or script."""

            import builtins
            import subprocess

            mutated_kwargs = ""
            for k, v in kwargs.items():
                mutated_kwargs += f"export {k}={v} && "

            attrs = [a[1] for a in self.argtypes]
            num_input_outputs = attrs.count(Lepton.INPUT_OUTPUT)
            num_outputs = attrs.count(Lepton.OUTPUT)

            if (num_input_outputs + num_outputs) != len(self.named_outputs):
                raise Exception(
                    "Expecting {} named outputs.".format(num_input_outputs + num_outputs)
                )

            if num_input_outputs != len(kwargs):
                raise Exception("Expecting {} keyword arguments.".format(num_input_outputs))

            output_string = ""
            if self.named_outputs:
                for output in self.named_outputs:
                    output_string += f" && echo COVALENT-LEPTON-OUTPUT-{output}: ${output}"

            if self.command:
                if isinstance(self.command, list):
                    self.command = " && ".join(self.command)
                self.command = self.command.format(**kwargs)
                cmd = ["/bin/bash", "-c", f"{mutated_kwargs} {self.command} {output_string}", "_"]
                cmd += args
                proc = subprocess.run(cmd, capture_output=True)
            elif self.library_name:
                mutated_args = ""
                for arg in args:
                    mutated_args += f'"{arg}" '

                cmd = f"{mutated_kwargs} source {self.library_name} && {self.function_name} {mutated_args} {output_string}"
                proc = subprocess.run(["/bin/bash", "-c", cmd], capture_output=True)
            else:
                raise AttributeError(
                    "Shell task does not have enough information to run."
                )  # pragma: no cover

            if proc.returncode != 0:
                raise Exception(proc.stderr.decode("utf-8").strip())

            return_vals = []
            if self.named_outputs:
                output_lines = proc.stdout.decode("utf-8").strip().split("\n")
                for idx, output in enumerate(self.named_outputs):
                    output_marker = f"COVALENT-LEPTON-OUTPUT-{output}: "
                    for line in output_lines:
                        if output_marker in line:
                            # TODO: For some reason cannot pickle this line
                            return_vals += [
                                getattr(builtins, self.argtypes[idx][0])(
                                    line.split(output_marker)[1]
                                )
                            ]
                            break

            if return_vals:
                return tuple(return_vals) if len(return_vals) > 1 else return_vals[0]
            else:
                return None

        if self.language in Lepton._LANG_PY:
            wrapper = python_wrapper
        elif self.language in Lepton._LANG_C:
            wrapper = c_wrapper
        elif self.language in Lepton._LANG_SHELL:
            wrapper = shell_wrapper
        else:
            raise ValueError(f"Language '{self.language}' is not supported.")

        # Attribute translation
        wrapper.__name__ = self.display_name or self.function_name or self.command
        wrapper.__qualname__ = (
            f"Lepton.{self.display_name}"
            if self.display_name
            else f"Lepton.{self.library_name.split('.')[0]}.{self.function_name}"
        )
        wrapper.__module__ += (
            ".console"
            if (self.language in Lepton._SCRIPTING_LANGUAGES and self.command)
            else f".{self.library_name.split('.')[0]}"
        )
        wrapper.__doc__ = (
            f"""Lepton interface for {self.language} function '{self.function_name}'."""
            if self.function_name
            else ""
        )

        return wrapper


def bash(
    _func: Optional[Callable] = None,
    *,
    display_name: Optional[str] = "",
    executor: Optional[
        Union[List[Union[str, "BaseExecutor"]], Union[str, "BaseExecutor"]]
    ] = DEFAULT_METADATA_VALUES["executor"],
    files: List[FileTransfer] = [],
    deps_bash: Union[DepsBash, List, str] = DEFAULT_METADATA_VALUES["deps"].get("bash", []),
    deps_pip: Union[DepsPip, list] = DEFAULT_METADATA_VALUES["deps"].get("pip", None),
    call_before: Union[List[DepsCall], DepsCall] = DEFAULT_METADATA_VALUES["call_before"],
    call_after: Union[List[DepsCall], DepsCall] = DEFAULT_METADATA_VALUES["call_after"],
) -> Callable:
    """Bash decorator which wraps a Python function as a Bash Lepton."""

    deps = {}

    if isinstance(deps_bash, DepsBash):
        deps["bash"] = deps_bash
    if isinstance(deps_bash, list) or isinstance(deps_bash, str):
        deps["bash"] = DepsBash(commands=deps_bash)

    if isinstance(deps_pip, DepsPip):
        deps["pip"] = deps_pip
    if isinstance(deps_pip, list):
        deps["pip"] = DepsPip(packages=deps_pip)

    if isinstance(call_before, DepsCall):
        call_before = [call_before]

    if isinstance(call_after, DepsCall):
        call_after = [call_after]

    def decorator_bash_lepton(func=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_dict = dict(zip(func.__code__.co_varnames[: func.__code__.co_argcount], args))
            arg_dict.update(kwargs)
            lepton_object = Lepton(
                "bash",
                command=func(*args, **kwargs),
                display_name=display_name,
                executor=executor,
                files=files,
                deps_bash=deps_bash,
                deps_pip=deps_pip,
                call_before=call_before,
                call_after=call_after,
            )
            return lepton_object()

        return wrapper

    if _func is None:
        return decorator_bash_lepton
    else:
        return decorator_bash_lepton(_func)
