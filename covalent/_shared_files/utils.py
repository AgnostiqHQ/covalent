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

"""General utils for Covalent."""

import importlib
import inspect
import socket
from datetime import timedelta
from typing import Any, Callable, Dict, Set, Tuple

import cloudpickle
from pennylane._device import Device

from . import logger
from .config import get_config
from .pickling import _qml_mods_pickle

app_log = logger.app_log
log_stack_info = logger.log_stack_info

DEFAULT_UI_ADDRESS = get_config("user_interface.address")
DEFAULT_UI_PORT = get_config("user_interface.port")


# Dictionary to map Dask clients to their scheduler addresses
_address_client_mapper = {}

_IMPORT_PATH_SEPARATOR = ":"


def get_ui_url(path):
    baseUrl = f"http://{DEFAULT_UI_ADDRESS}:{DEFAULT_UI_PORT}"
    return f"{baseUrl}{path}"


def get_random_available_port() -> int:
    """
    Return a random port that is available on the machine
    """
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def get_timedelta(time_limit: str) -> timedelta:
    """
    Get timedelta from a compatible time limit string passed to the lattice/electron decorator.

    Args:
        time_limit: The time limit string.
    Returns:
        timedelta: The `datetime.timedelta` object.
    """

    days, hours, minutes, seconds = time_limit.split("-")[0], *time_limit.split("-")[1].split(":")
    return timedelta(
        days=int(days),
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
    )


def reformat(t: int) -> str:
    """
    Reformat an integer to a readable time-like string. For example, if t = 1, return "01".

     Args:
         t: The integer to reformat.

     Returns:
         ref_string: The reformatted string.
    """

    return f"0{t}" if len(str(t)) == 1 else str(t)


def get_time(time_delta: timedelta) -> str:
    """
    Get a compatible time string from a timedelta object.

    Args:
        time_delta: The timedelta object.
    Returns:
        time_string: The compatible reformatted time string.
    """

    days = reformat(time_delta.days)
    hours = reformat(time_delta.seconds // 3600)
    minutes = reformat((time_delta.seconds // 60) % 60)
    seconds = reformat(time_delta.seconds % 60)
    return f"{days}-{hours}:{minutes}:{seconds}"


def filter_null_metadata(meta_dict: dict) -> Dict:
    """Filter out metadata that is None or empty."""
    return {k: v for k, v in meta_dict.items() if v}


def get_serialized_function_str(function):
    """
    Generates a string representation of a function definition
    including the decorators on it.

    Args:
        function: The function whose definition is to be convert to a string.

    Returns:
        function_str: The string representation of the function definition.
    """

    input_function = function
    # If a Lattice or electron object was passed as the function input, we need the
    # (deserialized) underlying function describing the lattice.
    while hasattr(input_function, "workflow_function"):
        input_function = input_function.workflow_function.get_deserialized()

    try:
        # function_str is the string representation of one function, with decorators, if any.
        function_str = inspect.getsource(input_function)
    except Exception:
        function_str = f"# {function.__name__} was not inspectable"

    return function_str + "\n\n"


def get_imports(func: Callable) -> Tuple[str, Set[str]]:
    """
    Given an input workflow function, find the imports that were used, and determine
        which ones are Covalent-related.

    Args:
        func: workflow function.

    Returns:
        A tuple consisting of a string of import statements and a set of names that
            Covalent-related modules have been imported as.
    """

    imports_str = ""
    cova_imports = set()
    for i, j in func.__globals__.items():
        if inspect.ismodule(j) or (
            inspect.isfunction(j) and j.__name__ in ["lattice", "electron"]
        ):
            if j.__name__ == i:
                import_line = f"import {j.__name__}\n"
            else:
                import_line = f"import {j.__name__} as {i}\n"

            if j.__name__ in ["covalent", "lattice", "electron"]:
                import_line = f"# {import_line}"
                cova_imports.add(i)

            imports_str += import_line

    return imports_str, cova_imports


def required_params_passed(func: Callable, kwargs: Dict) -> bool:
    """
    DEPRECATED: Check to see that values for all parameters without default values have been passed.

    Args:
        func: Callable function.
        kwargs: Parameter list with passed values.

    Returns:
        status: Whether all the parameters required for the callable function has been passed.
    """

    required_arg_set = set({})
    sig = inspect.signature(func)
    for param in sig.parameters.values():
        if param.default is param.empty:
            required_arg_set.add(str(param))

    return required_arg_set.issubset(set(kwargs.keys()))


def get_named_params(func, args, kwargs):
    ordered_params_dict = inspect.signature(func).parameters

    named_args = {}
    named_kwargs = {}

    for ind, parameter_dict in enumerate(ordered_params_dict.items()):
        param_name, param = parameter_dict

        if param.kind in [param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD]:
            if param_name in kwargs:
                named_kwargs[param_name] = kwargs[param_name]
            elif ind < len(args):
                named_args[param_name] = args[ind]
        elif param.kind == param.VAR_POSITIONAL:
            for i in range(ind, len(args)):
                named_args[f"arg[{i}]"] = args[i]
        elif param.kind in [param.KEYWORD_ONLY, param.VAR_KEYWORD]:
            for key, value in kwargs.items():
                if key != param_name:
                    named_kwargs[key] = value

    if len(args) > len(named_args):
        raise ValueError(
            f"Too many positional arguments given, expected {len(named_args)}, received {len(args)}"
        )

    if len(kwargs) > len(named_kwargs):
        extra_supplied_kwargs = ", ".join(sorted(set(kwargs.keys()) - set(named_kwargs.keys())))
        raise ValueError(f"Unexpected keyword arguments: {extra_supplied_kwargs}")

    return (named_args, named_kwargs)


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
