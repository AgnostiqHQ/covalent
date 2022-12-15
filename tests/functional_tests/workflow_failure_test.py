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

"""Test how Covalent handles task failures in a workflow"""

import time

import covalent as ct


def test_workflow_continues_after_node_failure():
    """Check that Covalent continues to dispatch runnable tasks even
    if an unrelated task fails.
    """

    @ct.electron
    def failing_task():
        assert False

    @ct.electron
    def double(x):
        import time

        time.sleep(1)
        return 2 * x

    # Graph consists of
    # 0 (failing)
    # 2 -> 1 -> 3 -> 4
    @ct.lattice
    def workflow(x):
        failing_task()
        return double(double(double(x)))

    dispatch_id = ct.dispatch(workflow)(1)

    time_to_wait = 8

    # This returns after the first task fails
    res = ct.get_result(dispatch_id, wait=True)
    tg = res.lattice.transport_graph
    status = tg.get_node_value(4, "status")

    while str(status) != "COMPLETED" and time_to_wait > 0:
        time_to_wait -= 1
        time.sleep(1)
        res = ct.get_result(dispatch_id, wait=True)
        tg = res.lattice.transport_graph
        status = tg.get_node_value(4, "status")

    assert tg.get_node_value(4, "output").get_deserialized() == 8
