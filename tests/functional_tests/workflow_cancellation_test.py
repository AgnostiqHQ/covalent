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

"""End-to-end tests of dispatch cancellation"""


import covalent as ct
import covalent._results_manager.results_manager as rm

TEST_RESULTS_DIR = "/tmp/results"


def test_cancel():
    """Test cancelling dispatch"""
    import time

    @ct.electron
    def sleeping_task(delay):
        import time

        time.sleep(delay)
        print("Slept for {delay} seconds")
        return delay

    @ct.lattice
    def workflow(x):
        res = sleeping_task(x)
        res2 = sleeping_task(res)
        res3 = sleeping_task(res2)
        return 1

    dispatch_id = ct.dispatch(workflow)(3)
    time.sleep(0.2)

    ct.cancel(dispatch_id)

    result = ct.get_result(dispatch_id, wait=True)
    assert result.status == ct.status.CANCELLED
    rm._delete_result(dispatch_id)


def test_cancel_task():
    """Test cancelling specific task"""
    import time

    @ct.electron
    def sleeping_task(delay):
        import time

        time.sleep(delay)
        print("Slept for {delay} seconds")
        return delay

    @ct.lattice
    def workflow(x):
        res = sleeping_task(x)
        res2 = sleeping_task(res)

        return 1

    dispatch_id = ct.dispatch(workflow)(3)
    time.sleep(0.1)

    ct.cancel(dispatch_id, task_ids=[2])

    result = ct.get_result(dispatch_id, wait=True)
    assert result.get_node_result(0)["status"] == ct.status.COMPLETED
    assert result.get_node_result(2)["status"] == ct.status.CANCELLED
    assert result.status == ct.status.CANCELLED
    rm._delete_result(dispatch_id)


def test_cancel_sublattice():
    """Test cancelling sublattice"""
    import time

    @ct.electron
    def sleeping_task(delay):
        import time

        time.sleep(delay)
        print("Slept for {delay} seconds")
        return delay

    @ct.electron
    @ct.lattice
    def sub_workflow(x):
        res = sleeping_task(x)
        res2 = sleeping_task(res)

        return 1

    @ct.lattice
    def workflow(x):
        return sub_workflow(3)

    dispatch_id = ct.dispatch(workflow)(3)
    time.sleep(0.5)

    ct.cancel(dispatch_id, task_ids=[0])

    result = ct.get_result(dispatch_id, wait=True)

    tg = result.lattice.transport_graph
    sub_dispatch_id = tg.get_node_value(0, "sub_dispatch_id")

    print("Sublattice dispatch id:", sub_dispatch_id)
    sub_res = ct.get_result(sub_dispatch_id)
    assert sub_res.status == ct.status.CANCELLED
