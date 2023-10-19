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

"""Testing methods to retrieve workflow artifacts"""

import pytest

import covalent as ct
from covalent._shared_files.exceptions import MissingLatticeRecordError


def test_granular_get_result():
    def add(a, b):
        return a + b

    @ct.electron
    def identity(a):
        return a

    sublattice_add = ct.lattice(add)

    @ct.lattice
    def workflow(a, b):
        res_1 = ct.electron(sublattice_add)(a=a, b=b)
        return identity(a=res_1)

    dispatch_id = ct.dispatch(workflow)(a=1, b=2)
    res_obj = ct.get_result(
        dispatch_id,
        wait=True,
        workflow_output=False,
        intermediate_outputs=False,
        sublattice_results=False,
    )

    assert res_obj.result is None

    res_obj = ct.get_result(
        dispatch_id, workflow_output=True, intermediate_outputs=False, sublattice_results=False
    )
    assert res_obj.result == 3

    assert res_obj.get_node_result(0)["sublattice_result"] is None

    res_obj = ct.get_result(
        dispatch_id, workflow_output=True, intermediate_outputs=False, sublattice_results=True
    )
    assert res_obj.result == 3

    assert res_obj.get_node_result(0)["sublattice_result"].result == 3
    assert res_obj.get_node_result(0)["output"] is None

    res_obj = ct.get_result(
        dispatch_id, workflow_output=True, intermediate_outputs=True, sublattice_results=False
    )
    assert res_obj.result == 3

    assert res_obj.get_node_result(0)["sublattice_result"] is None
    assert res_obj.get_node_result(0)["output"].get_deserialized() == 3


def test_get_result_nonexistent():
    with pytest.raises(MissingLatticeRecordError):
        result_object = ct.get_result("nonexistent", wait=False)
