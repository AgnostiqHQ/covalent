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
import os
from datetime import timedelta
from io import TextIOWrapper
from typing import Callable, Dict, List, Set, Tuple, Union

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


def get_serialized_function_str(function) -> str:
    """
    Generates a string representation of a function definition
    including the decorators on it.

    Args:
        function: The function whose definition is to be convert to a string.

    Returns:
        function_str: The string representation of the function definition, along with
            imports.
    """

    input_function = function
    # If a Lattice or electron object was passed as the function input, we need the
    # underlying function describing the lattice.
    while hasattr(input_function, "workflow_function"):
        input_function = input_function.workflow_function

    # Get external (to Covalent) imports that were used. And record what Covalent
    # has been imported as.
    imports, cova_imports = imports_from_sources()
    imports = list(imports)
    imports.sort()

    try:
        import_str = ""
        for import_statement in imports:
            import_str += f"{import_statement}\n"
        import_str += "\n"

        # inspect.getsource call gets the string representation of one function, with decorators, if any.
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
                if decorator_name in cova_imports:
                    for i in range(start - 1, end):
                        commented_lines.add(i)

        if len(commented_lines) > 0:
            function_str_list = function_str.split("\n")
            for i in range(len(function_str_list)):
                if i in commented_lines:
                    line = function_str_list[i].lstrip()
                    function_str_list[i] = f"# {function_str_list[i]}"
            function_str = "\n".join(function_str_list)

        function_str = import_str + function_str

    except Exception:
        function_str = f"# {function.__name__} was not inspectable"
    return function_str + "\n\n"


def imports_from_sources(external_only: bool = True) -> Tuple[Set[str], Set[str]]:
    """
    Scan in-scope modules and find imports and which imports are for covalent-related modules.

    Args:
        external_only: If True, only files outside the covalent and covalent_dispatcher
            modules are scanned.

    Returns:
        A 2-element tuple containing a set of import statements, and a set of names which
            covalent-related modules have been imported as.
    """

    imports = set()
    cova_imports = set()
    source_list = _scan_source_files(external_only)
    for source_string in source_list:
        try:
            imp, cova_imp = parse_source_for_imports(source_string, comment_cova=True)
            imports.update(imp)
            cova_imports.update(cova_imp)

        except Exception as e:
            # This is scanning all files that are utilized. We don't want any minor error, that
            # possibly could come from outside the Covalent code-base, to derail the process.
            app_log.debug(e)

    return imports, cova_imports


def _scan_source_files(external_only: bool = True) -> List[str]:
    """
    When called, this will scan and read all source files in scope, and return a list
        of strings, where each string is the contents of one source file.

    Args:
        external_only: If True, only files outside the covalent and covalent_dispatcher
            modules are scanned.

    Returns:
        A list of strings, where each string is the contents of one source file.
    """

    source_list = []
    scanned = set()

    for frame_info in inspect.stack():
        frame = frame_info.frame
        filename = inspect.getsourcefile(frame)

        top_level_module = ""
        if external_only:
            module = inspect.getmodule(frame)
            if module is not None:
                top_level_module = module.__name__.split(".")[0]

        if (
            filename is None  # This can happen with built-in types.
            or not os.path.exists(filename)
            or (external_only and top_level_module in ["covalent", "covalent_dispatcher"])
            or filename in scanned  # Already scanned.
        ):
            continue

        with open(filename, "r") as fh:
            source_list.append(fh.read())
        scanned.add(filename)

    return source_list


def parse_source_for_imports(
    source_string, comment_cova: bool = False
) -> Tuple[Set[str], Set[str]]:
    """
    Scan a source snippet and find imports. And find which imports are
        for covalent-related modules.

    Args:
        source_string: The source code snippet, as a string.
        comment_cova: If True, Covalent-related import emtries are pre-pended with "# ".

    Returns:
        A 2-element tuple containing a set of import statements, and a set of names which
            covalent-related modules have been imported as.
    """

    imports = set()
    cova_imports = set()
    parsed_source = ast.parse(source_string)

    for node in ast.iter_child_nodes(parsed_source):

        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue

        for subnode in node.names:

            cova_module = False
            import_string = ""
            if isinstance(node, ast.ImportFrom):
                if node.module is None:
                    # This happens for "from . import <module_name>.
                    continue
                import_string = f"from {node.module} "
                if node.module.split(".")[0] in ["covalent", "covalent_dispatcher"]:
                    cova_module = True

            import_string += f"import {subnode.name}"
            if subnode.asname is not None:
                import_string += f" as {subnode.asname}"

            if subnode.name.split(".")[0] in ["covalent", "covalent_dispatcher"]:
                cova_module = True

            if cova_module:
                if subnode.asname is not None:
                    cova_imports.add(subnode.asname)
                else:
                    cova_imports.add(subnode.name)

                if comment_cova:
                    import_string = f"# {import_string}"

            imports.add(import_string)

    return imports, cova_imports


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
