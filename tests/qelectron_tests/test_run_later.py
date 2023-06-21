# Copyright 2023 Agnostiq Inc.
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

"""
Tests for the `run_later()` method of QElectrons.
"""
import covalent as ct
from covalent.experimental import covalent_qelectron as cq
import pennylane as qml
import pytest

from .utils import get_named_measurement


def qubit_ansatz(param):
    qml.Hadamard(wires=[0])
    qml.CRX(param, wires=[0, 1])


DEVICES = ["default.qubit", "lightning.qubit"]

INTERFACES = [None, "torch", "tf", "jax"]

MEASUREMENTS = ["expval", "var", "sample"]


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("interface", INTERFACES)
@pytest.mark.parametrize("meas_name", MEASUREMENTS)
def test_output_types(device, interface, meas_name, wires=2):
    """
    Test that the output types of `run_later()` and `__call__()` are the same.

    NOTE: Pennylane tests cover correctness of `__call__()`.
    """
    dev = qml.device(device, wires=wires, shots=1024)
    op = qml.operation.Tensor(*(qml.PauliY(0), qml.PauliX(1)))
    qml_measurement = get_named_measurement(meas_name)

    def _circuit(param):
        qubit_ansatz(param)
        return qml_measurement(op)

    # create normal QNode
    qnode = qml.QNode(_circuit, dev, interface=interface)

    # create QElectron from QNode
    qiskit_exec = ct.executor.QiskitExecutor(device="local_sampler")
    qe = cq.qelectron(qnode, executors=qiskit_exec)

    _param = qml.numpy.array(0.5)

    res_qnode = qnode(_param)
    res_qe = qe(_param)

    # mimic typical use case, but grab only first result
    futs = [qe.run_later(_param) for _ in range(10)]
    res_qe_rl = [fut.result() for fut in futs][0]

    assert isinstance(res_qe, type(res_qnode))
    assert isinstance(res_qe_rl, type(res_qnode))
