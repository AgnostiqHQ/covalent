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

# pylint: disable=no-member

import pytest

import covalent as ct
import pennylane as qml
from numpy import isclose

EXECUTORS = [
    ct.executor.QiskitExecutor(device="local_sampler", shots=10_000),
    ct.executor.Simulator(),
]


@pytest.mark.parametrize("executor", EXECUTORS)
def test_qaoa(executor):
    """
    Test that the `run_later` produces the same result as the normal call for
    """
    from pennylane import qaoa
    from networkx import Graph

    wires = range(10)
    graph = Graph([(0, 1), (1, 2), (2, 0)])
    cost_h, mixer_h = qaoa.maxcut(graph)

    def qaoa_layer(gamma, alpha):
        qaoa.cost_layer(gamma, cost_h)
        qaoa.mixer_layer(alpha, mixer_h)

    @ct.qelectron(executors=executor)
    @qml.qnode(qml.device('lightning.qubit', wires=len(wires)))
    def circuit(params):
        for w in wires:
            qml.Hadamard(wires=w)
        qml.layer(qaoa_layer, 2, params[0], params[1])
        return qml.expval(cost_h)

    inputs = [[1, 1.], [1.2, 1]]
    output_1 = circuit(inputs.copy())
    output_2 = circuit.run_later(inputs.copy()).result()

    assert isclose(output_1, output_2, rtol=0.1), "Call and run later results are different"
