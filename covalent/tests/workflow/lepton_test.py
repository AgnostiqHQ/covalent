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

import ctypes
import inspect
import os
from contextlib import nullcontext

import pytest

from covalent._workflow.electron import Electron
from covalent._workflow.lepton import Lepton
from covalent.executor import LocalExecutor


class MockCCall:
    def __call__(*mock_args, **mock_kwargs):
        return None


class MockHandle:
    def __init__(self):
        self.argtypes = None
        self.restype = None

    def __getitem__(self, item):
        return MockCCall()


def test_lepton_init(mocker, monkeypatch):

    init_mock = mocker.patch("covalent._workflow.lepton.Electron.__init__", return_value=None)
    set_metadata_mock = mocker.patch(
        "covalent._workflow.lepton.Electron.set_metadata", return_value=None
    )
    wrap_mock = mocker.patch(
        "covalent._workflow.lepton.Lepton.wrap_task", return_value="wrapper function"
    )

    executor = LocalExecutor()
    lepton = Lepton(
        language="lang",
        library_name="libname",
        function_name="funcname",
        argtypes=[(int, "type")],
        executor=executor,
    )

    init_mock.assert_called_once_with("wrapper function")
    wrap_mock.assert_called_once_with()
    set_metadata_mock.assert_called_once_with("executor", executor)

    assert lepton.language == "lang"
    assert lepton.library_name == "libname"
    assert lepton.function_name == "funcname"
    assert lepton.argtypes == [("int", "type")]

    assert isinstance(lepton, Electron)


def test_lepton_attributes():
    def filter_attributes(attributes):
        return [a for a in attributes if not (a[0].startswith("__") and a[0].endswith("__"))]

    electron_attributes = filter_attributes(inspect.getmembers(Electron))
    lepton_attributes = filter_attributes(inspect.getmembers(Lepton))

    expected_attributes = [
        ("INPUT", 0),
        ("OUTPUT", 1),
        ("INPUT_OUTPUT", 2),
        ("_LANG_PY", ["Python", "python"]),
        ("_LANG_C", ["C", "c"]),
        ("_LANG_SHELL", ["bash", "shell"]),
        ("wrap_task", Lepton.wrap_task),
    ]

    assert sorted(electron_attributes + expected_attributes) == sorted(lepton_attributes)


@pytest.fixture
def init_mock(mocker):
    return mocker.patch("covalent._workflow.lepton.Lepton.__init__", return_value=None)


@pytest.mark.parametrize("language", ["python", "c", "unsupported"])
def test_wrap_task(mocker, init_mock, language):
    lepton = Lepton()
    init_mock.assert_called_once()

    lepton.language = language
    lepton.library_name = "mylib"
    lepton.function_name = "myfunc"

    context = pytest.raises(ValueError) if language == "unsupported" else nullcontext()
    with context:
        task = lepton.wrap_task()

    if language == "unsupported":
        return

    assert task.__code__.co_name == f"{language}_wrapper"
    assert task.__name__ == "myfunc"
    assert task.__qualname__ == "Lepton.mylib.myfunc"
    assert task.__module__ == "covalent._workflow.lepton.mylib"
    assert task.__doc__ == f"Lepton interface for {language} function 'myfunc'."


@pytest.mark.parametrize(
    "library_name,function_name",
    [
        ("test_module", "test_func"),
        ("test_module.py", "test_func"),
        ("bad_module", ""),
        ("bad_module.py", ""),
        ("test_module", "bad_func"),
    ],
)
def test_python_wrapper(mocker, init_mock, library_name, function_name):
    python_test_module_str = """\
def test_func(x, y):
    return x + y\
"""

    with open("test_module.py", "w") as f:
        f.write(python_test_module_str)
        f.flush()

    lepton = Lepton()
    lepton.language = "python"
    lepton.library_name = library_name
    lepton.function_name = function_name
    task = lepton.wrap_task()

    init_mock.assert_called_once_with()

    if library_name.startswith("bad_module"):
        context = pytest.raises((ModuleNotFoundError, FileNotFoundError, AttributeError))
    elif function_name == "bad_func":
        context = pytest.raises(AttributeError)
    else:
        context = nullcontext()

    with context:
        result = task(1, 2)

    os.remove("test_module.py")

    if library_name.startswith("bad_module") or function_name == "bad_func":
        return

    assert result == 3


@pytest.mark.parametrize(
    "library_name,function_name,argtypes,named_outputs",
    [
        ("test_library.sh", "add", [(int, Lepton.OUTPUT)], ["result"]),
        ("test_library.sh", "add", [], ["result"]),
    ],
)
def test_shell_wrapper(mocker, init_mock, library_name, function_name, argtypes, named_outputs):
    sh_script_src = """#! /bin/bash

export result=""

add() {
    result=`expr $1 + $2`
}
"""

    with open("test_library.sh", "w") as f:
        f.write(sh_script_src)
        f.flush()

    lepton = Lepton()
    lepton.language = "bash"
    lepton.library_name = library_name
    lepton.function_name = function_name
    lepton.argtypes = argtypes

    task = lepton.wrap_task()

    init_mock.assert_called_once_with()

    if len(argtypes) == 0:
        context = pytest.raises(ValueError)
    else:
        context = nullcontext()

    with context:
        result = task(5, 7, named_outputs=named_outputs)

    os.remove("test_library.sh")

    if not argtypes:
        return

    assert result == (12,)


class MockType:
    def __call__(self, *args, **kwargs):
        return list(args)

    def __mul__(self, other):
        return self

    def __rmul__(self, other):
        return self


class MockPointer:
    def __init__(self):
        self.__name__ = "LP_c_int"
        self._type_ = MockType()

    def __getitem__(self, item):
        return None


@pytest.mark.parametrize(
    "library_name,argtypes,args,kwargs,response",
    [
        ("test_empty", [], [], {}, None),
        ("test_kwarg", [], [], {"bad_kwarg": "bad_value"}, None),
        ("scalar_input", [(ctypes.c_int, Lepton.INPUT)], [1], {}, None),
        ("list_input", [(ctypes.POINTER(ctypes.c_int), Lepton.INPUT)], [[1]], {}, None),
    ],
)
def test_c_wrapper(mocker, init_mock, library_name, argtypes, args, kwargs, response):
    lepton = Lepton()
    lepton.language = "C"
    lepton.library_name = library_name
    lepton.function_name = "test_func"
    lepton.argtypes = [(arg[0].__name__, arg[1]) for arg in argtypes]

    task = lepton.wrap_task()
    init_mock.assert_called_once_with()

    mock_handle = MockHandle()
    cdll_mock = mocker.patch("ctypes.CDLL", return_value=mock_handle)
    func_call_mock = mocker.patch(f"{__name__}.MockCCall.__call__", return_value=response)

    c_int_mock = mocker.patch("ctypes.c_int", return_value=1)
    c_pointer_mock = mocker.patch("ctypes.POINTER", return_value=MockPointer())

    if kwargs:
        context = pytest.raises(ValueError)
    else:
        context = nullcontext()

    with context:
        result = task(*args, **kwargs)

    if library_name == "test_kwarg":
        return

    cdll_mock.assert_called_once_with(library_name)
    assert mock_handle.restype is None

    if library_name == "test_empty":
        func_call_mock.assert_called_once_with()
        assert result is None
    elif library_name == "scalar_input":
        func_call_mock.assert_called_once_with(1)
        c_int_mock.assert_called_once_with(1)
        assert result is None
    elif library_name == "list_input":
        func_call_mock.assert_called_once_with([1])

    # TODO: Still need to test variable translations
