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

# pylint: disable=no-member

from typing import Callable, List, Tuple

import pennylane as qml
from pennylane import numpy as np


def simple_circuit(param):
    """
    A tiny, reusable Pennylane circuit.
    """
    qml.RX(param, wires=0)
    qml.Hadamard(wires=1)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.operation.Tensor(*(qml.PauliY(0), qml.PauliX(1))))


def get_hamiltonian_circuit() -> Tuple[Callable, List[int], int]:
    """
    A Pennylane circuit that returns the `expval` of a Hamiltonian.
    """

    symbols = ["H", "H"]
    coordinates = np.array([0.0, 0.0, -0.6614, 0.0, 0.0, 0.6614])
    H, num_qubits = qml.qchem.molecular_hamiltonian(symbols, coordinates)

    n_electrons = 2
    hf_state = qml.qchem.hf_state(n_electrons, num_qubits)
    _, doubles = qml.qchem.excitations(n_electrons, num_qubits)

    def manual_double_excitation(phi, wires):
        """
        Manually implement decomposition of `qml.DoubleExcitation` gate.

        TODO: replace with `qml.DoubleExcitation` call once template support is merged.
        """
        qml.CNOT(wires=[wires[2], wires[3]])
        qml.CNOT(wires=[wires[0], wires[2]])
        qml.Hadamard(wires=wires[3])
        qml.Hadamard(wires=wires[0])
        qml.CNOT(wires=[wires[2], wires[3]])
        qml.CNOT(wires=[wires[0], wires[1]])
        qml.RY(phi / 8, wires=wires[1])
        qml.RY(-phi / 8, wires=wires[0])
        qml.CNOT(wires=[wires[0], wires[3]])
        qml.Hadamard(wires=wires[3])
        qml.CNOT(wires=[wires[3], wires[1]])
        qml.RY(phi / 8, wires=wires[1])
        qml.RY(-phi / 8, wires=wires[0])
        qml.CNOT(wires=[wires[2], wires[1]])
        qml.CNOT(wires=[wires[2], wires[0]])
        qml.RY(-phi / 8, wires=wires[1])
        qml.RY(phi / 8, wires=wires[0])
        qml.CNOT(wires=[wires[3], wires[1]])
        qml.Hadamard(wires=wires[3])
        qml.CNOT(wires=[wires[0], wires[3]])
        qml.RY(-phi / 8, wires=wires[1])
        qml.RY(phi / 8, wires=wires[0])
        qml.CNOT(wires=[wires[0], wires[1]])
        qml.CNOT(wires=[wires[2], wires[0]])
        qml.Hadamard(wires=wires[0])
        qml.Hadamard(wires=wires[3])
        qml.CNOT(wires=[wires[0], wires[2]])
        qml.CNOT(wires=[wires[2], wires[3]])

    def circuit(params):
        """
        Applies circuit operations.
        """
        for i, occ in enumerate(hf_state):
            if occ == 1:
                qml.PauliX(wires=i)
        for param in params:
            manual_double_excitation(param, wires=list(range(num_qubits)))
        return qml.expval(H)

    return circuit, doubles, num_qubits


def cyclic_selector(qscript, executors):
    """
    A QCluster selector that cycle through sub-executors in a cyclic fashion.

    NOTE: set the `i` attribute to 0 before using this selector.

    TODO: remove once default cluster selectors are implemented.
    """
    ex = executors[cyclic_selector.i % len(executors)]
    cyclic_selector.i += 1
    return ex


def arg_vector(size):
    """
    A random `tensor` of size `(size,)` with values in `[0, 2 * pi]`.
    """
    return qml.numpy.random.uniform(0, 2 * np.pi, size=(size,))


def weight_vector(size):
    """
    A QAOA weights vector that matches args from `arg_vector(size)`.
    """
    return [arg_vector(2 * size) for _ in range(size)]
