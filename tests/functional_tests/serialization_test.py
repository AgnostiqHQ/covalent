# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import covalent
import covalent as cova
from covalent import electron as etron
from covalent._shared_files.utils import get_serialized_function_str
from covalent._workflow.lattice import Lattice

executor = covalent.executor._executor_manager.list_executors(print_names=False)[0]


def non_electron(x):
    return x


@cova.electron(executor=executor)
def electron_function(x):
    return x


@etron
@cova.lattice
def sub_lattice_function(y):
    return y


@covalent.lattice
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


def test_non_electron_serialization():
    """Test that 'normal' functions are successfully serialized."""

    function_string = get_serialized_function_str(non_electron)
    expected_string = "\n".join(
        [
            "def non_electron(x):",
            "    return x",
        ]
    )
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_electron_serialization():
    """Test that an electron function is successfully serialized."""

    function_string = get_serialized_function_str(electron_function)
    expected_string = "\n".join(
        [
            "@cova.electron(executor=executor)",
            "def electron_function(x):",
            "    return x",
        ]
    )
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_lattice_serialization():
    """Test that a lattice function is successfully serialized."""

    function_string = get_serialized_function_str(lattice_function)
    expected_string = "\n".join(
        [
            "@covalent.lattice",
            "def lattice_function(input_a, input_b):",
            "    a = electron_function(x=input_a)",
            "    b = sub_lattice_function(y=input_b)",
            "    return a + b",
        ]
    )
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_lattice_object_serialization():
    """Test that a Lattice object, based on a sub-lattice, is successsfully serialized."""

    lattice_obj = Lattice(sub_lattice_function)
    function_string = get_serialized_function_str(lattice_obj)
    expected_string = "\n".join(
        [
            "@etron",
            "@cova.lattice",
            "def sub_lattice_function(y):",
            "    return y",
        ]
    )
    expected_string += "\n\n\n"
    assert function_string == expected_string


def test_nested_electron():
    """Test a nested electron."""

    function_string = get_serialized_function_str(nested_electron)
    expected_string = "\n".join(
        [
            "@covalent.electron",
            "@covalent.lattice",
            "@etron",
            "@cova.lattice",
            "@covalent.electron",
            "def nested_electron(z):",
            "    return z",
        ]
    )
    expected_string += "\n\n\n"
    assert function_string == expected_string
