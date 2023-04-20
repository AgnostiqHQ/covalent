# Copyright 2023 Agnostiq Inc.
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

"""Test different types of workflows."""

import enum

import pytest

import covalent as ct


class WORKFLOW_TYPES(str, enum.Enum):
    HORIZONTAL = "HORIZONTAL"
    VERTICAL = "VERTICAL"
    HAGRID = "HAGRID"


@pytest.mark.parametrize(
    "workflow_type, parallel, serial, n",
    [
        (WORKFLOW_TYPES.HORIZONTAL, True, False, 8),
        (WORKFLOW_TYPES.VERTICAL, False, True, 10),
        (WORKFLOW_TYPES.HAGRID, True, True, 10),
    ],
)
def test_heterogenous_workflows(workflow_type, parallel, serial, n):
    """Test different types of workflows."""

    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def combine(x):
        return sum(x)

    @ct.lattice
    def workflow(n, parallel=False, serial=False):
        vals = []
        result = 186282
        nodes = range(n)

        if parallel and not serial:
            for _ in nodes:
                vals.append(identity(1))
            result = combine(vals)

        elif serial and not parallel:
            for _ in nodes:
                result = identity(result)
        elif serial and parallel:
            for i in nodes:
                for _ in nodes:
                    if i == 0:
                        vals.append(identity(1))
                    else:
                        vals.append(identity(result))
                result = combine(vals)
        return result

    dispatch_id = ct.dispatch(workflow)(n, parallel, serial)
    res = ct.get_result(dispatch_id, wait=True)

    if workflow_type == WORKFLOW_TYPES.HORIZONTAL:
        assert res.result == 8
    elif workflow_type == WORKFLOW_TYPES.VERTICAL:
        assert res.result == 186282
    elif workflow_type == WORKFLOW_TYPES.HAGRID:
        assert res.result == 23579476910
