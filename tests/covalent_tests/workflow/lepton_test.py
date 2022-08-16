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

"""Unit tests for leptons."""

import inspect
import os
from contextlib import nullcontext
from ctypes import POINTER, c_int32
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile

import pytest

from covalent import DepsBash, TransportableObject
from covalent._file_transfer.file_transfer import HTTP, File, FileTransfer, Order
from covalent._workflow.lepton import Lepton, bash
from covalent.executor import LocalExecutor

test_py_module = """
def entrypoint(x: int, y: int) -> int:
    return x + y
"""
temp_py_file = NamedTemporaryFile("w")
with temp_py_file as f:
    f.write(test_py_module)

library_path = os.path.join(os.getcwd(), temp_py_file.name)

test_c_source = """
#include "test.h"

void test_entry(int x, int *y, int *z)
{
        *y += x;
        *z = 5;
}
"""

test_c_header = """
void test_entry(int x, int *y, int *z);
"""

temp_c_source_file, temp_c_header_file = NamedTemporaryFile("w"), NamedTemporaryFile("w")

with temp_c_source_file as f:
    f.write(test_c_source)

with temp_c_header_file as f:
    f.write(test_c_header)

c_source_path, c_header_path = os.path.join(os.getcwd(), temp_c_source_file.name), os.path.join(
    os.getcwd(), temp_c_header_file.name
)

proc = Popen(
    f"gcc -shared -fPIC -o libtest.so {c_source_path}", shell=True, stdout=PIPE, stderr=PIPE
)


# TODO: Still need to validate behavior for:
#        - files
#        - deps_bash
#        - deps_pip
#        - call_before
#        - call_after
@pytest.mark.parametrize(
    "language,library_name,function_name,argtypes,command,named_outputs,valid",
    [
        # Call a Python function in a Python library
        ("python", "pylib", "pyfunc", [(int, "type")], "", [], True),
        # Invoke a Python command
        ("python", "", "", [(int, "type")], "pycmd", [], True),
        # Call a C function in a compiled library
        ("c", "clib", "cfunc", [(c_int32, "type")], "", [], True),
        # Invoke a Bash function in a shell script
        ("bash", "script", "shfunc", [(int, "type")], "", ["output"], True),
        # Invoke a Bash command
        ("bash", "", "", [(int, "type")], "shcmd", ["output"], True),
        # Provide conflicting parameters for Python
        ("python", "pylib", "", [(int, "type")], "pycmd", [], False),
        # Provide insufficient parameters for Python
        ("python", "pylib", "", [(int, "type")], "", [], False),
        ("python", "", "", [], "", [], False),
        # Provide a command to a non-scripting language
        ("c", "", "", [(int, "type")], "ccmd", [], False),
        # Attempt to use named outputs with a non-scripting language
        ("c", "clib", "cfunc", [], "", ["output"], False),
    ],
)
def test_lepton_init(
    mocker, language, library_name, function_name, argtypes, command, named_outputs, valid
):
    electron_init_mock = mocker.patch(
        "covalent._workflow.lepton.Electron.__init__", return_value=None
    )
    wrap_mock = mocker.patch(
        "covalent._workflow.lepton.Lepton.wrap_task", return_value="wrapper function"
    )
    set_metadata_mock = mocker.patch(
        "covalent._workflow.lepton.Electron.set_metadata", return_value=None
    )

    executor = LocalExecutor()

    with nullcontext() if valid else pytest.raises(ValueError):
        lepton = Lepton(
            language=language,
            library_name=library_name,
            function_name=function_name,
            argtypes=argtypes,
            command=command,
            named_outputs=named_outputs,
            display_name="disp name",
            executor=executor,
        )

        electron_init_mock.assert_called_once_with("wrapper function")
        wrap_mock.assert_called_once_with()
        assert set_metadata_mock.call_count == 5

        assert lepton.language == language
        assert lepton.function_name == function_name
        assert lepton.argtypes == [(arg[0].__name__, arg[1]) for arg in argtypes]
        if language in Lepton._SCRIPTING_LANGUAGES:
            assert lepton.command == command
            assert lepton.named_outputs == named_outputs
        assert lepton.display_name == "disp name"


def test_lepton_languages(
    supported_languages=("C", "c", "python", "Python", "bash", "shell"),
    unsupported_languages=(
        "R",
        "r",
        "Erlang",
        "erlang",
        "Haskell",
        "haskell",
        "Julia",
        "julia",
        "C++",
        "c++",
        "Fortan",
        "fortran",
    ),
):
    for language in supported_languages:
        assert language in Lepton._LANG_C or Lepton._LANG_PY or Lepton._LANG_SHELL

    for language in unsupported_languages:
        with pytest.raises(ValueError):
            Lepton(language)


@pytest.mark.parametrize("is_from_file_remote, is_to_file_remote", [(False, False)])
@pytest.mark.parametrize("order", (Order.BEFORE, Order.AFTER))
def test_local_file_transfer_support(is_from_file_remote, is_to_file_remote, order):
    """
    Test for local file transfer
    """

    mock_from_file = File("file:///home/source.csv", is_remote=is_from_file_remote)
    mock_to_file = File("file:///home/dest.csv", is_remote=is_to_file_remote)

    mock_file_transfer = FileTransfer(from_file=mock_from_file, to_file=mock_to_file, order=order)
    mock_lepton_with_files = Lepton("python", command="mockcmd", files=[mock_file_transfer])
    call_before_deps = mock_lepton_with_files.get_metadata("call_before")
    call_after_deps = mock_lepton_with_files.get_metadata("call_after")

    pre_hook_call_dep, file_transfer_call_dep = mock_file_transfer.cp()

    if mock_file_transfer.order == "before":
        # There should be two call before call deps: pre hook + file transfer
        assert len(call_before_deps) == 2
        assert len(call_after_deps) == 0

        assert inspect.getsource(
            TransportableObject.from_dict(
                call_before_deps[0]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(pre_hook_call_dep)
        assert inspect.getsource(
            TransportableObject.from_dict(
                call_before_deps[1]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(file_transfer_call_dep)

    if mock_file_transfer.order == "after":
        # There should be one call before call deps: pre hook
        assert len(call_before_deps) == 1
        # There should be one call after call deps: file transfer
        assert len(call_after_deps) == 1

        assert inspect.getsource(
            TransportableObject.from_dict(
                call_before_deps[0]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(pre_hook_call_dep)
        assert inspect.getsource(
            TransportableObject.from_dict(
                call_after_deps[0]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(file_transfer_call_dep)


@pytest.mark.parametrize("order", (Order.BEFORE, Order.AFTER))
def test_http_file_transfer(order):
    """
    Test for http file transfer
    """
    mock_from_file = File("http://example.com/source.csv")
    mock_to_file = File("file:///home/dest.csv")
    mock_file_download = FileTransfer(from_file=mock_from_file, to_file=mock_to_file, order=order)
    mock_lepton_with_files = Lepton("python", command="mockcmd", files=[mock_file_download])

    # Test that HTTP upload strategy is not currently implemented
    with pytest.raises(NotImplementedError):
        Lepton(
            "python",
            command="mockcmd",
            files=[FileTransfer(from_file=mock_to_file, to_file=mock_from_file, strategy=HTTP())],
        )

    deps = mock_lepton_with_files.get_metadata("deps")
    assert deps["bash"]["attributes"]["commands"] == []
    assert deps.get("pip") is None
    call_before = mock_lepton_with_files.get_metadata("call_before")
    call_after = mock_lepton_with_files.get_metadata("call_after")

    pre_hook_call_dep, file_transfer_call_dep = mock_file_download.cp()

    if mock_file_download.order == "before":
        # There should be two call before call deps: pre hook + file transfer
        assert len(call_before) == 2
        assert len(call_after) == 0

        assert inspect.getsource(
            TransportableObject.from_dict(
                call_before[0]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(pre_hook_call_dep)
        assert inspect.getsource(
            TransportableObject.from_dict(
                call_before[1]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(file_transfer_call_dep)

    if mock_file_download.order == "after":
        # There should be one call before call deps: pre hook
        assert len(call_before) == 1
        # There should be one call after call deps: file transfer
        assert len(call_after) == 1

        assert inspect.getsource(
            TransportableObject.from_dict(
                call_before[0]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(pre_hook_call_dep)
        assert inspect.getsource(
            TransportableObject.from_dict(
                call_after[0]["attributes"]["apply_fn"]
            ).get_deserialized()
        ) == inspect.getsource(file_transfer_call_dep)


@pytest.fixture
def init_mock(mocker):
    return mocker.patch("covalent._workflow.lepton.Lepton.__init__", return_value=None)


@pytest.mark.parametrize(
    "language,display_name,cmd",
    [
        ("python", "", False),
        ("python", "", True),
        ("python", "pydisplay", False),
        ("python", "pydisplay", True),
        ("c", "", False),
        ("c", "cdisplay", False),
        ("shell", "", False),
        ("shell", "sdisplay", True),
        ("unsupported", "", ""),
    ],
)
def test_wrap_task(mocker, init_mock, language, display_name, cmd):
    lepton = Lepton()
    init_mock.assert_called_once()

    lepton.language = language
    if cmd:
        lepton.library_name = ""
        lepton.function_name = ""
        lepton.command = "mycommand"
    else:
        lepton.library_name = "mylib"
        lepton.function_name = "myfunc"
        lepton.command = ""
    lepton.display_name = display_name

    context = pytest.raises(ValueError) if language == "unsupported" else nullcontext()
    with context:
        task = lepton.wrap_task()

    if language == "unsupported":
        return

    assert task.__code__.co_name == f"{language}_wrapper"
    assert task.__name__ == display_name or ("myfunc" if not cmd else "mycommand")
    assert task.__qualname__ == f"Lepton.{display_name}" if display_name else "Lepton.mylib.myfunc"
    assert (
        task.__module__ == "covalent._workflow.lepton.console"
        if cmd
        else "covalent._workflow.lepton.mylib"
    )
    if not cmd:
        assert task.__doc__ == f"Lepton interface for {language} function 'myfunc'."


# TODO: Needs improvement
def test_python_wrapper():
    """
    Test that the python wrapper can call a foreign python function
    """
    mock_lepton = Lepton(library_name=test_py_module, function_name="entrypoint")
    wrapper = mock_lepton.wrap_task()
    assert callable(wrapper)


# TODO: Needs improvement
def test_c_wrapper():
    """
    Test that the C wrapper can call a C function specified in a shared library
    """
    mock_lepton = Lepton(language="C", library_name="libtest.so", function_name="test_entry")
    wrapper = mock_lepton.wrap_task()
    with pytest.raises(ValueError):
        wrapper(a=1, b=2, c=3)  # wrapper should not accept kwargs
    assert callable(wrapper)


sh_script_simple = """#!/bin/bash
print_hostname() {
    hostname
}
"""

sh_script_output = """#!/bin/bash
add() {
    result=`expr $1 + $2`
}
"""

sh_script_io = """#!/bin/bash
modify() {
    let x=$x+5
}
"""


@pytest.mark.parametrize(
    "library_name,library_body,function_name,argtypes,command,named_outputs,args,kwargs,expected_return,valid",
    [
        # Valid usage examples
        # Call a bash function
        ("test_library.sh", sh_script_simple, "print_hostname", [], "", [], [], {}, None, True),
        # Call a bash function with two inputs and a return value (either syntax valid)
        (
            "test_library.sh",
            sh_script_output,
            "add",
            [(int, Lepton.OUTPUT)],
            "",
            ["result"],
            [5, 7],
            {},
            12,
            True,
        ),
        (
            "test_library.sh",
            sh_script_output,
            "add",
            [(int, Lepton.INPUT), (int, Lepton.INPUT), (int, Lepton.OUTPUT)],
            "",
            ["result"],
            [5, 7],
            {},
            12,
            True,
        ),
        # Call a bash function with an input-output value
        (
            "test_library.sh",
            sh_script_io,
            "modify",
            [(int, Lepton.INPUT_OUTPUT)],
            "",
            ["x"],
            [],
            {"x": 3},
            8,
            True,
        ),
        # Call a bash command
        ("", "", "", [], "hostname", [], [], {}, None, True),
        # Call a list of bash commands
        ("", "", "", [], ["hostname", "whoami"], [], [], {}, None, True),
        # Call a bash command with an input
        ("", "", "", [], "touch /tmp/$1", [], ["debug.txt"], {}, None, True),
        ("", "", "", [(str, Lepton.INPUT)], "touch /tmp/$1", [], ["debug.txt"], {}, None, True),
        # Call a bash command with an input-output
        ("", "", "", [(str, Lepton.INPUT_OUTPUT)], "x=a$x", ["x"], [], {"x": "b"}, "ab", True),
        # Call a bash command with an output
        ("", "", "", [(int, Lepton.OUTPUT)], "x=17", "x", [], {}, 17, True),
        # Call a bash command with multiple outputs
        (
            "",
            "",
            "",
            [(int, Lepton.OUTPUT), (int, Lepton.OUTPUT)],
            "x=17 && y=18",
            ["x", "y"],
            [],
            {},
            (17, 18),
            True,
        ),
        # Invalid usage examples
        # Insufficient named outputs
        (
            "",
            "",
            "",
            [(int, Lepton.OUTPUT), (int, Lepton.OUTPUT)],
            "x=17 && y=18",
            "x",
            [],
            {},
            (17, 18),
            False,
        ),
        # Input outputs not specified by kwargs
        ("", "", "", [(int, Lepton.INPUT_OUTPUT)], "x=a$x", ["x"], [], {}, "ab", False),
        # Bash command returns non-zero exit code
        ("", "", "", [], "exit 1", [], [], {}, None, False),
        # TODO: Add more usage which should throw errors
    ],
)
def test_shell_wrapper(
    mocker,
    init_mock,
    library_name,
    library_body,
    function_name,
    argtypes,
    command,
    named_outputs,
    expected_return,
    args,
    kwargs,
    valid,
):

    if library_name:
        with open(library_name, "w") as f:
            f.write(library_body)
            f.flush()

    lepton = Lepton()
    lepton.language = "bash"
    lepton.library_name = library_name
    lepton.function_name = function_name
    lepton.argtypes = [(arg[0].__name__, arg[1]) for arg in argtypes]
    lepton.command = command
    lepton.named_outputs = named_outputs
    lepton.display_name = "name"

    task = lepton.wrap_task()

    init_mock.assert_called_once_with()

    with nullcontext() if valid else pytest.raises(Exception):
        result = task(*args, **kwargs)

    if library_name:
        os.remove(library_name)

    if not valid:
        return

    assert result == expected_return
