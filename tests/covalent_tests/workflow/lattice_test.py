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

"""Unit tests for lattice"""

import covalent as ct


def test_lattice_draw(mocker):
    mock_send_draw_req = mocker.patch("covalent_ui.result_webhook.send_draw_request")

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.draw(2)

    mock_send_draw_req.assert_called_once()


def test_lattice_build_graph_populates_executor_data():
    """Test that task nodes have nonempty executor_data"""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(executor="local")
    def workflow(x):
        return task(x)

    workflow.build_graph(1)
    tg = workflow.transport_graph

    assert tg._graph.nodes[0]["metadata"]["executor_data"]
