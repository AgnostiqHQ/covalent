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

"""Unit tests for electron"""

import covalent as ct
from covalent._shared_files.context_managers import active_lattice_manager


@ct.electron
def task_1(a):
    import time

    time.sleep(3)
    return a**2


@ct.electron
def task_2(x, y):
    return x * y


@ct.electron
def task_3(b):
    return b**3


@ct.lattice
def workflow():
    res_1 = task_1(2)
    res_2 = task_2(res_1, 3)
    res_3 = task_3(5).wait_for(res_1)

    return task_2(res_2, res_3)


def test_wait_for_building():
    """Test to check whether the graph is built correctly with `wait_for`."""

    workflow.build_graph()
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["wait_for"]
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["edge_name"] == "!waiting_edge"


def test_wait_for_post_processing():
    """Test to check post processing with `wait_for` works fine."""

    workflow.post_processing = True
    workflow.electron_outputs = [(0, 4), (1, 2), (2, 12), (3, 3), (4, 125), (5, 5), (6, 1500)]

    with active_lattice_manager.claim(workflow):
        assert workflow.workflow_function() == 1500
