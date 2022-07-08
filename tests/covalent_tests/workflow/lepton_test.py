import os
import pytest

from subprocess import Popen, PIPE
from ctypes import c_int32, POINTER
from tempfile import NamedTemporaryFile
from covalent._workflow.lepton import Lepton

test_py_module = """
def entrypoint(x: int, y: int) -> int:
    return x + y
"""
temp_py_file = NamedTemporaryFile('w')
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

c_source_path, c_header_path = os.path.join(os.getcwd(), temp_c_source_file.name), os.path.join(os.getcwd(),
                                                                                                temp_c_header_file.name)

proc = Popen(f"gcc -shared -fPIC -o libtest.so {c_source_path}", shell=True, stdout=PIPE, stderr=PIPE)


def test_init_lepton():
    mock_py_lepton = Lepton(language="python", library_name=library_path, function_name="entrypoint")

    assert mock_py_lepton.language == "python"
    assert mock_py_lepton.library_name == temp_py_file.name
    assert mock_py_lepton.function_name == "entrypoint"
    assert mock_py_lepton.argtypes == []

    mock_c_lepton = Lepton(
                language="C",
                library_name=c_source_path, function_name="test_entry",
                argtypes=[
                    (c_int32, Lepton.INPUT),
                    (POINTER(c_int32), Lepton.INPUT_OUTPUT),
                    (POINTER(c_int32), Lepton.OUTPUT)
                    ],
                )

    assert mock_c_lepton.language == "C"
    assert mock_c_lepton.library_name == temp_c_source_file.name
    assert mock_c_lepton.function_name == "test_entry"
    assert mock_c_lepton.argtypes == [("c_int", 0), ("LP_c_int", 2), ("LP_c_int", 1)]


def test_lepton_languages(
        supported_languages=("C", "c", "python", "Python"),
        unsupported_languages=("R", "r", "Erlang", "erlang", "Haskell", "haskell")
):
    for language in supported_languages:
        assert language in Lepton._LANG_C or Lepton._LANG_PY

    for language in unsupported_languages:
        with pytest.raises(ValueError):
            Lepton(language=language)


def test_file_transfer_support():
    """
    Test file transfer in a lepton
    """


def test_python_wrapper():
    pass


def test_c_wrapper():
    pass
