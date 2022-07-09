import inspect
import os
from ctypes import POINTER, c_int32
from subprocess import PIPE, Popen
from tempfile import NamedTemporaryFile

import pytest

from covalent import DepsBash
from covalent._file_transfer.file_transfer import HTTP, File, FileTransfer, Order
from covalent._workflow.lepton import Lepton

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


def test_init_lepton():
    mock_py_lepton = Lepton(
        language="python", library_name=library_path, function_name="entrypoint"
    )

    assert mock_py_lepton.language == "python"
    assert mock_py_lepton.library_name == temp_py_file.name
    assert mock_py_lepton.function_name == "entrypoint"
    assert mock_py_lepton.argtypes == []

    mock_c_lepton = Lepton(
        language="C",
        library_name=c_source_path,
        function_name="test_entry",
        argtypes=[
            (c_int32, Lepton.INPUT),
            (POINTER(c_int32), Lepton.INPUT_OUTPUT),
            (POINTER(c_int32), Lepton.OUTPUT),
        ],
    )

    assert mock_c_lepton.language == "C"
    assert mock_c_lepton.library_name == temp_c_source_file.name
    assert mock_c_lepton.function_name == "test_entry"
    assert mock_c_lepton.argtypes == [("c_int", 0), ("LP_c_int", 2), ("LP_c_int", 1)]


def test_lepton_languages(
    supported_languages=("C", "c", "python", "Python"),
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
        assert language in Lepton._LANG_C or Lepton._LANG_PY

    for language in unsupported_languages:
        with pytest.raises(ValueError):
            Lepton(language=language)


@pytest.mark.parametrize("is_from_file_remote, is_to_file_remote", [(False, False)])
@pytest.mark.parametrize("order", (Order.BEFORE, Order.AFTER))
def test_local_file_transfer_support(is_from_file_remote, is_to_file_remote, order):
    """
    Test for local file transfer
    """

    mock_from_file = File("file:///home/source.csv", is_remote=is_from_file_remote)
    mock_to_file = File("file:///home/dest.csv", is_remote=is_to_file_remote)

    mock_file_transfer = FileTransfer(from_file=mock_from_file, to_file=mock_to_file, order=order)
    mock_lepton_with_files = Lepton(files=[mock_file_transfer])
    call_before_deps = mock_lepton_with_files.get_metadata("call_before")
    call_after_deps = mock_lepton_with_files.get_metadata("call_after")

    if mock_file_transfer.order == "before":
        # No file transfer should be done after executing the lepton
        assert call_after_deps == []

    if mock_file_transfer.order == "after":
        # No file transfer should be done before executing the lepton
        assert call_before_deps == []

    # The defined file transfer strategies should not be mutated by the lepton
    for call in call_before_deps:
        assert inspect.getsource(call.apply_fn.get_deserialized()) == inspect.getsource(
            mock_file_transfer.cp()
        )
    for call in call_after_deps:
        assert inspect.getsource(call.apply_fn.get_deserialized()) == inspect.getsource(
            mock_file_transfer.cp()
        )


@pytest.mark.parametrize(
    "is_from_file_remote, is_to_file_remote", [(False, True), (True, False), (True, True)]
)
@pytest.mark.parametrize("order", (Order.BEFORE, Order.AFTER))
def test_http_file_transfer(is_from_file_remote, is_to_file_remote, order):
    """
    Test for http file transfer
    """
    mock_from_file = File("http://example.com/source.csv")
    mock_to_file = File("file:///home/dest.csv")
    mock_file_download = FileTransfer(from_file=mock_from_file, to_file=mock_to_file, order=order)
    mock_lepton_with_files = Lepton(files=[mock_file_download])

    # Test that HTTP upload strategy is not currently implemented
    with pytest.raises(NotImplementedError):
        Lepton(
            files=[FileTransfer(from_file=mock_to_file, to_file=mock_from_file, strategy=HTTP())]
        )

    deps = mock_lepton_with_files.get_metadata("deps")
    assert isinstance(deps["bash"], DepsBash)
    assert deps.get("pip") is None
    call_before_deps = mock_lepton_with_files.get_metadata("call_before")
    call_after_deps = mock_lepton_with_files.get_metadata("call_after")

    if mock_file_download.order == "before":
        # No file transfer should be done after executing the lepton
        assert call_after_deps == []

    if mock_file_download.order == "after":
        # No file transfer should be done before executing the lepton
        assert call_before_deps == []

    # The defined file transfer strategies should not be mutated by the lepton
    for call in call_before_deps:
        assert inspect.getsource(call.apply_fn.get_deserialized()) == inspect.getsource(
            mock_file_download.cp()
        )
    for call in call_after_deps:
        assert inspect.getsource(call.apply_fn.get_deserialized()) == inspect.getsource(
            mock_file_download.cp()
        )


def test_python_wrapper():
    """
    Test that the python wrapper can call a foreign python function
    """
    mock_lepton = Lepton(library_name=test_py_module)
    wrapper = mock_lepton.wrap_task()
    assert callable(wrapper)


def test_c_wrapper():
    """
    Test that the C wrapper can call a C function specified in a shared library
    """
    mock_lepton = Lepton(language="C", library_name="libtest.so")
    wrapper = mock_lepton.wrap_task()
    with pytest.raises(ValueError):
        wrapper(a=1, b=2, c=3)  # wrapper should not accept kwargs
    assert callable(wrapper)
