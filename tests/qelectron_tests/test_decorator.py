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

import pennylane as qml
import pytest
from numpy import isclose

import covalent as ct

EXECUTORS = [
    ct.executor.QiskitExecutor(device="local_sampler", shots=10_000),
]


@pytest.mark.parametrize("executor", EXECUTORS)
def test_argument_types_single_qexecutor(executor):
    """
    Test that `ct.qelectron` accepts a variety of argument combinations.
    """

    results = []

    # Initialize qelectron by decorating a qnode.
    dev = qml.device("default.qubit", wires=2)

    @ct.qelectron(executors=executor)
    @qml.qnode(device=dev)
    def simple_circuit_1(param):
        """
        A tiny, reusable Pennylane circuit.
        """
        qml.RX(param, wires=0)
        qml.Hadamard(wires=1)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.operation.Tensor(*(qml.PauliY(0), qml.PauliX(1))))

    qelectron = simple_circuit_1
    results.append(qelectron(0.5))

    # Initialize qelectron by passing a qnode.
    @qml.qnode(device=dev)
    def simple_circuit_2(param):
        """
        A tiny, reusable Pennylane circuit.
        """
        qml.RX(param, wires=0)
        qml.Hadamard(wires=1)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.operation.Tensor(*(qml.PauliY(0), qml.PauliX(1))))

    qelectron = ct.qelectron(simple_circuit_2, executors=executor)
    results.append(qelectron(0.5))

    assert isinstance(results[0], type(results[1])), f"Results {results!r} are not the same type"
    assert isclose(results[0], results[1], 0.1), f"Results {results!r} are not close"
