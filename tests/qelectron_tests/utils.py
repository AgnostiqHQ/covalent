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
