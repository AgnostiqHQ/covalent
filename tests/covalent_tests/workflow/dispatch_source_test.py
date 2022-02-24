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

"""Unit tests for writing the dispatch_source.py file"""

import pytest

from covalent._results_manager.result import _filter_cova_decorators

COVA_IMPORTS = {"covalent", "lattice", "electron", "ct", "cova", "etron"}


INPUT1 = "\n".join(
    [
        "@covalent.electron(",
        '    executor="local"',
        ")",
        "def identity(x):",
        "    return x",
        "",
        "@covalent.electron",
        "@covalent.lattice",
        "@covalent.electron(",
        '    executor="local"',
        ")",
        "def double(x):",
        "    return 2*x",
    ]
)

INPUT2 = INPUT1.replace("covalent", "ct")
INPUT3 = INPUT1.replace("covalent", "cova")
INPUT4 = INPUT1.replace("ct.electron", "electron")
INPUT5 = INPUT1.replace("ct.electron", "etron")
INPUT6 = INPUT1.replace("ct.lattice", "lattice")

OUTPUT1 = "\n".join(
    [
        "# @covalent.electron(",
        '#     executor="local"',
        "# )",
        "def identity(x):",
        "    return x",
        "",
        "# @covalent.electron",
        "# @covalent.lattice",
        "# @covalent.electron(",
        '#     executor="local"',
        "# )",
        "def double(x):",
        "    return 2*x",
    ]
)

OUTPUT2 = OUTPUT1.replace("covalent", "ct")
OUTPUT3 = OUTPUT1.replace("covalent", "cova")
OUTPUT4 = OUTPUT1.replace("ct.electron", "electron")
OUTPUT5 = OUTPUT1.replace("ct.electron", "etron")
OUTPUT6 = OUTPUT1.replace("ct.lattice", "lattice")


@pytest.mark.parametrize(
    "input_str, expected_str",
    [
        (INPUT1, OUTPUT1),
        (INPUT2, OUTPUT2),
        (INPUT3, OUTPUT3),
        (INPUT4, OUTPUT4),
        (INPUT5, OUTPUT5),
        (INPUT6, OUTPUT6),
    ],
)
def test_filter_cova_decorators(
    input_str,
    expected_str,
):
    """Test the filtering out of Covalent-related decorators."""

    output_str = _filter_cova_decorators(input_str, COVA_IMPORTS)

    assert output_str == expected_str
