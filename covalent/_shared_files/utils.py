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

import ast
import inspect
from datetime import timedelta
from io import TextIOWrapper
from typing import Callable, Dict, Set, Union

from . import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


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


def get_serialized_function_str(function):
    """
    Generates a string representation of a function definition
    including the decorators on it.

    Args:
        function: The function whose definition is to be convert to a string.

    Returns:
        function_str: The string representation of the function definition.
    """

    imports = _get_imports_from_source()
    ct_decorators = _get_cova_imports(imports)

    input_function = function
    # If a Lattice or electron object was passed as the function input, we need the
    # underlying function describing the lattice.
    while hasattr(input_function, "workflow_function"):
        input_function = input_function.workflow_function

    try:
        # function_str is the string representation of one function, with decorators, if any.
        function_str = inspect.getsource(input_function)

        # Check if the function has covalent decorators that need to be commented out.
        commented_lines = set()
        parsed_source = ast.parse(function_str)
        for node in ast.iter_child_nodes(parsed_source):
            for decorator in node.decorator_list:
                start = decorator.lineno
                end = decorator.end_lineno
                decorator_name = ""
                if hasattr(decorator, "id"):
                    decorator_name = decorator.id
                elif hasattr(decorator, "func"):
                    decorator_name = decorator.func.value.id
                else:
                    decorator_name = decorator.value.id
                if decorator_name in ct_decorators:
                    for i in range(start - 1, end):
                        commented_lines.add(i)

        function_str_list = function_str.split("\n")
        for i in range(len(function_str_list)):
            if i in commented_lines:
                line = function_str_list[i].lstrip()
                function_str_list[i] = f"# {function_str_list[i]}"
        function_str = "\n".join(function_str_list)
    except Exception:
        function_str = f"# {function.__name__} was not inspectable"
    return function_str + "\n\n"


def _get_cova_imports(imports_set: Set[Union[ast.Import, ast.ImportFrom]]) -> Set[str]:
    """Get a set of Covalent-related imports (and aliases) from a set of imports.

    Args:
        imports_set: A complete set of modules that have been imported.

    Returns:
        imports: A set of Covalent-related imports, inluding any aliases.
    """

    ct_imports = set()
    for node in imports_set:
        if isinstance(node, ast.Import):
            for i in range(len(node.names)):
                if node.names[i].name == "covalent":
                    if node.names[i].asname is None:
                        ct_imports.add("covalent")
                    else:
                        ct_imports.add(node.names[i].asname)
        elif isinstance(node, ast.ImportFrom):
            if node.module == "covalent":
                for i in range(len(node.names)):
                    if node.names[i].asname is None:
                        ct_imports.add(node.names[i].name)
                    else:
                        ct_imports.add(node.names[i].asname)

    return ct_imports


def _get_imports_from_source(
    source: Union[str, TextIOWrapper] = "",
    is_filename: bool = True,
    imports: set = set(),
) -> Set[Union[ast.Import, ast.ImportFrom]]:
    """Get (or add to) a set of imports from a source file.

    Args:
        source: The input source code (as a string), filename or file-handler object. If empty
            all files in scope are scanned.
        is_filename: If input source is a non-empty string, this denotes whether it is the source code
            itself, or a filename.
        imports: If non-empty, any imports found are added to this set and returned.

    Returns:
        imports: A set of imports (ast.node objects) found in the specified module code file.
    """

    if isinstance(source, str):
        if source == "":
            for frame_info in inspect.stack():
                frame = frame_info.frame
                try:
                    source = inspect.getsource(frame)
                    imports = _get_imports_from_source(
                        source=source, is_filename=False, imports=imports
                    )
                except (IndentationError, OSError) as e:
                    # This is scanning all files that are utilized. We don't want any minor error, that
                    # possibly could come from outside the Covalent code-base, to derail the process.
                    app_log.debug(e)
        elif is_filename:
            with open(source, "r") as fh:
                source = fh.read()
        else:
            # source is the actual source as a str object
            pass
    elif isinstance(source, TextIOWrapper):
        source = source.read()
    else:
        raise TypeError

    try:
        parsed_source = ast.parse(source)
        for node in ast.iter_child_nodes(parsed_source):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.add(node)
    except IndentationError as e:
        app_log.debug(e)

    return imports


def required_params_passed(func: Callable, kwargs: Dict) -> bool:
    """Check to see that values for all parameters without default values have been passed.

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
