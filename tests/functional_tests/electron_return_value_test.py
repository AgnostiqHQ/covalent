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

"""Tests for verifying electron operability inside lattice"""

import pytest

import covalent as ct
from covalent._results_manager.results_manager import _delete_result, get_result


@ct.electron
def identity(x):
    return x


@ct.lattice
def arithmetic_test_1(a, operand):
    a = identity(x=a)

    if operand == "+":
        return a + 1
    elif operand == "-":
        return a - 1
    elif operand == "*":
        return a * 1
    elif operand == "/":
        return a / 1


@ct.lattice
def arithmetic_test_1_rev(a, operand):
    a = identity(x=a)

    if operand == "+":
        return 1 + a
    elif operand == "-":
        return 1 - a
    elif operand == "*":
        return 1 * a
    elif operand == "/":
        return 1 / a


@ct.lattice
def arithmetic_test_2(a, b, operand):
    a = identity(x=a)
    b = identity(x=b)

    if operand == "+":
        return a + b
    elif operand == "-":
        return a - b
    elif operand == "*":
        return a * b
    elif operand == "/":
        return a / b


@ct.lattice
def type_conversion_test_numbers(a, type_to):
    res = identity(x=a)
    if type_to == "int":
        return isinstance(int(res), int)
    elif type_to == "float":
        return isinstance(float(res), float)
    elif type_to == "complex":
        return isinstance(complex(res), complex)


@ct.lattice
def type_conversion_test_iterables(a, type_to):
    res = identity(x=a)
    if type_to == "list":
        return isinstance(list(res), list)
    elif type_to == "tuple":
        return isinstance(tuple(res), tuple)


@ct.lattice
def type_conversion_test_dict(a):
    res = identity(x=a)
    return isinstance(dict(res), dict)


@pytest.mark.parametrize("test_operand,expected", [("+", 3), ("-", 1), ("*", 2), ("/", 2.0)])
def test_arithmetic_1(test_operand, expected):
    """Test arithmetic operations"""

    dispatch_id = ct.dispatch(arithmetic_test_1)(a=2, operand=test_operand)

    res = get_result(dispatch_id, wait=True)
    _delete_result(dispatch_id)

    assert res.result == expected


@pytest.mark.parametrize("test_operand,expected", [("+", 3), ("-", -1), ("*", 2), ("/", 0.5)])
def test_arithmetic_1_rev(test_operand, expected):
    """Test reverse arithmetic operations"""

    dispatch_id = ct.dispatch(arithmetic_test_1_rev)(a=2, operand=test_operand)

    res = get_result(dispatch_id, wait=True)
    _delete_result(dispatch_id)

    assert res.result == expected


@pytest.mark.parametrize(
    "test_b,test_operand,expected", [(3, "+", 5), (3, "-", -1), (3, "*", 6), (4, "/", 0.5)]
)
def test_arithmetic_2(test_b, test_operand, expected):
    """Test arithmetic operations"""

    dispatch_id = ct.dispatch(arithmetic_test_2)(a=2, b=test_b, operand=test_operand)

    res = get_result(dispatch_id, wait=True)
    print(res)
    _delete_result(dispatch_id)

    assert res.result == expected


@pytest.mark.parametrize("test_type_to", ["int", "float", "complex"])
def test_type_conversion_numbers(test_type_to):
    """Test type conversion for number types"""

    dispatch_id = ct.dispatch(type_conversion_test_numbers)(a=2, type_to=test_type_to)

    res = get_result(dispatch_id, wait=True)
    _delete_result(dispatch_id)

    assert res.result


@pytest.mark.parametrize("test_type_to", ["list", "tuple"])
def test_type_conversion_iterables(test_type_to):
    """Test type conversion for iterables"""

    dispatch_id = ct.dispatch(type_conversion_test_iterables)(a=[2], type_to=test_type_to)

    res = get_result(dispatch_id, wait=True)
    _delete_result(dispatch_id)

    assert res.result


def test_type_conversion_dict():
    """Test type conversion for dictionary"""

    dispatch_id = ct.dispatch(type_conversion_test_dict)(a={"x": 2})

    res = get_result(dispatch_id, wait=True)
    _delete_result(dispatch_id)

    assert res.result
