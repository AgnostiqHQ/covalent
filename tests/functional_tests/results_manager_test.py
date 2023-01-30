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

"""Testing methods to retrieve workflow artifacts"""

import covalent as ct


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


def test_get_workflow_output():
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

    assert ct.get_workflow_output(dispatch_id).get_deserialized() == 3


def test_get_node_output():
    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow(a, b):
        return add(a, b)

    dispatch_id = ct.dispatch(workflow)(a=1, b=2)
    res_obj = ct.get_result(
        dispatch_id,
        wait=True,
        workflow_output=False,
        intermediate_outputs=False,
        sublattice_results=False,
    )

    assert ct.get_node_output(dispatch_id, 0).get_deserialized() == 3
