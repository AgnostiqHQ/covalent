# Copyright 2023 Agnostiq Inc.
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

    assert res.status == "COMPLETED"
