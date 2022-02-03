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

import pytest

import covalent
import covalent as cova

# These imports are here solely to check that they are commented out in the serialized function string.
import covalent._workflow
from covalent import electron as etron
from covalent._shared_files.config import set_config
from covalent._shared_files.utils import get_serialized_function_str
from covalent._workflow.lattice import Lattice

executor = covalent.executor._executor_manager.list_executors(print_names=False)[0]


def non_electron(x):
    return x


@cova.electron(backend=executor)
def electron_function(x):
    return x


@etron
@cova.lattice(
    results_dir="./",
    dispatcher="super long fake dispatcher to test really long arguments                                                                                                                                                                                end_fake_dispatcher_name",
)
def sub_lattice_function(y):
    return y


@covalent.lattice(results_dir="./")
def lattice_function(input_a, input_b):
    a = electron_function(x=input_a)
    b = sub_lattice_function(y=input_b)
    return a + b


@covalent.electron
@covalent.lattice
@etron
@cova.lattice
@covalent.electron
def nested_electron(z):
    return z


covalent_imports = [
    "# from covalent import electron as etron",
    "# from covalent._shared_files.config import set_config",
    "# from covalent._shared_files.utils import get_serialized_function_str",
    "# from covalent._workflow.lattice import Lattice",
    "# import covalent",
    "# import covalent as cova",
    "# import covalent._workflow",
]

pytest_imports = [
    "from _pytest import fixtures",
    "from _pytest import nodes",
    "from _pytest import timing",
    "from _pytest._code import ExceptionInfo",
    "from _pytest._code import filter_traceback",
    "from _pytest._code import getfslineno",
    "from _pytest._code.code import ExceptionChainRepr",
    "from _pytest._code.code import ExceptionInfo",
    "from _pytest._code.code import TerminalRepr",
    "from _pytest._io import TerminalWriter",
    "from _pytest._io.saferepr import saferepr",
    "from _pytest.compat import NOTSET",
    "from _pytest.compat import REGEX_TYPE",
    "from _pytest.compat import STRING_TYPES",
    "from _pytest.compat import ascii_escaped",
    "from _pytest.compat import final",
    "from _pytest.compat import get_default_arg_names",
    "from _pytest.compat import get_real_func",
    "from _pytest.compat import getimfunc",
    "from _pytest.compat import getlocation",
    "from _pytest.compat import importlib_metadata",
    "from _pytest.compat import is_async_function",
    "from _pytest.compat import is_generator",
    "from _pytest.compat import safe_getattr",
    "from _pytest.compat import safe_isclass",
    "from _pytest.config import Config",
    "from _pytest.config import ExitCode",
    "from _pytest.config import PytestPluginManager",
    "from _pytest.config import UsageError",
    "from _pytest.config import directory_arg",
    "from _pytest.config import hookimpl",
    "from _pytest.config.argparsing import Parser",
    "from _pytest.deprecated import FSCOLLECTOR_GETHOOKPROXY_ISINITPATH",
    "from _pytest.fixtures import FixtureManager",
    "from _pytest.fixtures import FuncFixtureInfo",
    "from _pytest.main import Session",
    "from _pytest.mark import MARK_GEN",
    "from _pytest.mark import ParameterSet",
    "from _pytest.mark.structures import Mark",
    "from _pytest.mark.structures import MarkDecorator",
    "from _pytest.mark.structures import get_unpacked_marks",
    "from _pytest.mark.structures import normalize_mark_list",
    "from _pytest.nodes import Collector",
    "from _pytest.nodes import Item",
    "from _pytest.nodes import Node",
    "from _pytest.outcomes import Exit",
    "from _pytest.outcomes import Skipped",
    "from _pytest.outcomes import TEST_OUTCOME",
    "from _pytest.outcomes import exit",
    "from _pytest.outcomes import fail",
    "from _pytest.outcomes import skip",
    "from _pytest.pathlib import ImportMode",
    "from _pytest.pathlib import ImportPathMismatchError",
    "from _pytest.pathlib import absolutepath",
    "from _pytest.pathlib import bestrelpath",
    "from _pytest.pathlib import import_path",
    "from _pytest.pathlib import parts",
    "from _pytest.pathlib import visit",
    "from _pytest.reports import CollectReport",
    "from _pytest.reports import TestReport",
    "from _pytest.runner import SetupState",
    "from _pytest.runner import collect_one_node",
    "from _pytest.store import Store",
    "from _pytest.warning_types import PytestCollectionWarning",
    "from _pytest.warning_types import PytestConfigWarning",
    "from _pytest.warning_types import PytestUnhandledCoroutineWarning",
    "from callers import _Result",
    "from callers import _legacymulticall",
    "from callers import _multicall",
    "from collections import Counter",
    "from collections import defaultdict",
    "from exceptions import PrintHelp as PrintHelp",
    "from exceptions import UsageError as UsageError",
    "from findpaths import determine_setup",
    "from functools import lru_cache",
    "from functools import partial",
    "from hooks import HookImpl",
    "from hooks import _HookCaller",
    "from hooks import _HookRelay",
    "from hooks import normalize_hookimpl_opts",
    "from pathlib import Path",
    "from pluggy import HookimplMarker",
    "from pluggy import HookspecMarker",
    "from pluggy import PluginManager",
    "from pytest import console_main",
    "from reports import BaseReport",
    "from reports import CollectErrorRepr",
    "from reports import CollectReport",
    "from reports import TestReport",
    "from types import TracebackType",
    "from typing import Any",
    "from typing import Callable",
    "from typing import Dict",
    "from typing import FrozenSet",
    "from typing import Generator",
    "from typing import Generic",
    "from typing import IO",
    "from typing import Iterable",
    "from typing import Iterator",
    "from typing import List",
    "from typing import Mapping",
    "from typing import Optional",
    "from typing import Sequence",
    "from typing import Set",
    "from typing import TYPE_CHECKING",
    "from typing import TextIO",
    "from typing import Tuple",
    "from typing import Type",
    "from typing import TypeVar",
    "from typing import Union",
    "from typing import cast",
    "from typing import overload",
    "import _pytest",
    "import _pytest._code",
    "import _pytest.deprecated",
    "import _pytest.hookspec",
    "import argparse",
    "import attr",
    "import bdb",
    "import collections.abc",
    "import contextlib",
    "import copy",
    "import enum",
    "import fnmatch",
    "import functools",
    "import importlib",
    "import inspect",
    "import itertools",
    "import os",
    "import py",
    "import pytest",
    "import re",
    "import shlex",
    "import sys",
    "import types",
    "import warnings",
]


def test_non_electron_serialization():
    """Test that 'normal' functions are successfully serialized."""

    function_lines = [
        "def non_electron(x):",
        "    return x",
    ]

    set_config("sdk.full_dispatch_source", "false")
    function_string = get_serialized_function_str(non_electron)
    expected_string = "\n".join(function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string

    set_config("sdk.full_dispatch_source", "true")
    function_string = get_serialized_function_str(non_electron)
    expected_string = "\n".join(covalent_imports + pytest_imports + [""] + function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_electron_serialization():
    """Test that an electron function is successfully serialized."""

    set_config("sdk.full_dispatch_source", "false")
    function_string = get_serialized_function_str(electron_function)
    function_lines = [
        "@cova.electron(backend=executor)",
        "def electron_function(x):",
        "    return x",
    ]
    expected_string = "\n".join(function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string

    set_config("sdk.full_dispatch_source", "true")
    function_string = get_serialized_function_str(electron_function)
    function_lines = [
        "# @cova.electron(backend=executor)",
        "def electron_function(x):",
        "    return x",
    ]
    expected_string = "\n".join(covalent_imports + pytest_imports + [""] + function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_lattice_serialization():
    """Test that a lattice function is successfully serialized."""

    set_config("sdk.full_dispatch_source", "false")
    function_string = get_serialized_function_str(lattice_function)
    function_lines = [
        '@covalent.lattice(results_dir="./")',
        "def lattice_function(input_a, input_b):",
        "    a = electron_function(x=input_a)",
        "    b = sub_lattice_function(y=input_b)",
        "    return a + b",
    ]
    expected_string = "\n".join(function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string

    set_config("sdk.full_dispatch_source", "true")
    function_string = get_serialized_function_str(lattice_function)
    function_lines = [
        '# @covalent.lattice(results_dir="./")',
        "def lattice_function(input_a, input_b):",
        "    a = electron_function(x=input_a)",
        "    b = sub_lattice_function(y=input_b)",
        "    return a + b",
    ]
    expected_string = "\n".join(covalent_imports + pytest_imports + [""] + function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_lattice_object_serialization():
    """Test that a Lattice object, based on a sub-lattice, is successsfully serialized."""

    lattice_obj = Lattice(sub_lattice_function)

    set_config("sdk.full_dispatch_source", "false")
    function_string = get_serialized_function_str(lattice_obj)
    function_lines = [
        "@etron",
        "@cova.lattice(",
        '    results_dir="./",',
        '    dispatcher="super long fake dispatcher to test really long arguments                                                                                                                                                                                end_fake_dispatcher_name",',
        ")",
        "def sub_lattice_function(y):",
        "    return y",
    ]
    expected_string = "\n".join(function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string

    set_config("sdk.full_dispatch_source", "true")
    function_string = get_serialized_function_str(lattice_obj)
    function_lines = [
        "# @etron",
        "# @cova.lattice(",
        '#     results_dir="./",',
        '#     dispatcher="super long fake dispatcher to test really long arguments                                                                                                                                                                                end_fake_dispatcher_name",',
        "# )",
        "def sub_lattice_function(y):",
        "    return y",
    ]
    expected_string = "\n".join(covalent_imports + pytest_imports + [""] + function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_nested_electron():
    """Test a nested electron."""

    set_config("sdk.full_dispatch_source", "false")
    function_string = get_serialized_function_str(nested_electron)
    function_lines = [
        "@covalent.electron",
        "@covalent.lattice",
        "@etron",
        "@cova.lattice",
        "@covalent.electron",
        "def nested_electron(z):",
        "    return z",
    ]
    expected_string = "\n".join(function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string

    set_config("sdk.full_dispatch_source", "true")
    function_string = get_serialized_function_str(nested_electron)
    function_lines = [
        "# @covalent.electron",
        "# @covalent.lattice",
        "# @etron",
        "# @cova.lattice",
        "# @covalent.electron",
        "def nested_electron(z):",
        "    return z",
    ]
    expected_string = "\n".join(covalent_imports + pytest_imports + [""] + function_lines)
    expected_string += "\n\n\n"
    assert function_string == expected_string
