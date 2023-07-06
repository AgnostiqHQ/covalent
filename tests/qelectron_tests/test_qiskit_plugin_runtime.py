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

import itertools

import pennylane as qml
import pytest
from pennylane import numpy as np

import covalent as ct
from covalent._shared_files.config import get_config

from .utils import get_hamiltonian_circuit, cyclic_selector

EXECUTOR_CLASSES = [
    ct.executor.QiskitExecutor,
]

QISKIT_RUNTIME_BACKENDS = [
    "ibmq_qasm_simulator",
    "simulator_statevector",
    "simulator_mps",
]

SHOTS = 10_000


@pytest.mark.parametrize("single_job", [True, False])
@pytest.mark.parametrize("executor_class", EXECUTOR_CLASSES)
@pytest.mark.parametrize("backend", QISKIT_RUNTIME_BACKENDS)
def test_qiskit_runtime_hamiltonian(backend, executor_class, single_job):
    """
    Check correctness of runtime executor result against normal QNode.
    """
    name = executor_class.__name__

    # Skip runtime test if no IBMQ token.
    if not get_config("qelectron")[name]["ibmqx_token"]:
        pytest.skip("IBMQ token not set in covalent config file.")

    ham_circuit, doubles, num_qubits = get_hamiltonian_circuit()

    dev = qml.device("default.qubit", wires=num_qubits, shots=SHOTS)

    # TODO: Has to be done this way for correctness. Why can't use `qml.QNode`?
    @qml.qnode(dev, diff_method="parameter-shift")
    def circuit(params):
        return ham_circuit(params)

    qexecutor = executor_class(device="sampler", single_job=single_job, backend=backend)
    qelectron = ct.qelectron(circuit, executors=qexecutor)

    params = np.random.uniform(low=-np.pi / 2, high=np.pi / 2, size=len(doubles))

    # Compute expectation values.
    val_1 = circuit(params)
    val_2 = qelectron(params)

    # Assert type agreement.
    assert isinstance(val_2, type(val_1))

    # Assert value agreement.
    # Assert value agreement.
    msg = (f"QElectron output ({val_2!r}) differs from "
           f"QNode output ({val_1!r}) by >10% (shots={SHOTS}).")
    assert np.isclose(val_1, val_2, rtol=0.10), msg


@pytest.mark.parametrize("single_job_tuple", list(itertools.product([True, False], repeat=3)))
@pytest.mark.parametrize("executor_class", EXECUTOR_CLASSES)
def test_qiskit_runtime_hamiltonian_cluster(single_job_tuple, executor_class):
    # pylint: disable=too-many-locals
    """
    Check correctness of runtime CLUSTER executor result against normal QNode.
    """
    name = executor_class.__name__

    # Skip runtime test if no IBMQ token.
    if not get_config("qelectron")[name]["ibmqx_token"]:
        pytest.skip("IBMQ token not set in covalent config file.")

    ham_circuit, doubles, num_qubits = get_hamiltonian_circuit()

    dev = qml.device("default.qubit", wires=num_qubits, shots=SHOTS)

    # TODO: Has to be done this way for correctness. Why can't use `qml.QNode`?
    @qml.qnode(dev, diff_method="parameter-shift")
    def circuit(params):
        return ham_circuit(params)

    # Set function attribute.
    cyclic_selector.i = 0

    # Define the quantum executors cluster.
    p_1, p_2, p_3 = single_job_tuple
    qcluster = ct.executor.QCluster(
        executors=[
            ct.executor.QiskitExecutor(
                device="sampler",
                single_job=p_1,
                backend="ibmq_qasm_simulator"
            ),
            ct.executor.QiskitExecutor(
                device="sampler",
                single_job=p_2,
                backend="simulator_statevector"
            ),
            ct.executor.QiskitExecutor(
                device="sampler",
                single_job=p_3,
                backend="simulator_mps"
            )
        ],
        selector=cyclic_selector
    )

    # Define a QElectron that uses the executor cluster.
    qelectron = ct.qelectron(circuit, executors=qcluster)

    params = np.random.uniform(low=-np.pi / 2, high=np.pi / 2, size=len(doubles))

    # Compute expectation values.
    val_1 = circuit(params)
    val_2 = qelectron(params)

    # Assert type agreement.
    assert isinstance(val_2, type(val_1))

    # Assert value agreement.
    msg = (f"QElectron output ({val_2!r}) differs from "
           f"QNode output ({val_1!r}) by >10% (shots={SHOTS}).")
    assert np.isclose(val_1, val_2, rtol=0.1), msg
