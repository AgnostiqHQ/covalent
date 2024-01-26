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

import itertools

import pennylane as qml
import pytest
from pennylane import numpy as np

import covalent as ct
from covalent._shared_files.config import get_config

from ..utils import arg_vector, cyclic_selector, get_hamiltonian_circuit, weight_vector

EXECUTOR_CLASSES = [
    ct.executor.QiskitExecutor,
]

QISKIT_RUNTIME_BACKENDS = [
    "ibmq_qasm_simulator",
    "simulator_statevector",
    "simulator_mps",
]

SHOTS = 10_000


@pytest.fixture(autouse=True, scope="module")
def ensure_ibmqx_token():
    """
    Ensure that the IBMQX token is set in the config file.
    """
    token_name = "ibmqx_token"
    tokens = {}
    qelectron_config = get_config("qelectron")
    for k, val in qelectron_config.items():
        # Exit if a global `ibmqx_token` is set.
        if k == "ibmqx_token" and val:
            return

        # Here, `k` is the name of an executor class.
        # Check if executors class config includes `"ibmqx_token"`.
        if isinstance(val, dict) and token_name in val:
            tokens[k] = val[token_name]

    for cls in EXECUTOR_CLASSES:
        k = cls.__name__
        if not tokens[k]:
            pytest.skip(f"Missing '{token_name}' for {k} in covalent config.")


@pytest.mark.parametrize("single_job", [True, False])
@pytest.mark.parametrize("executor_class", EXECUTOR_CLASSES)
@pytest.mark.parametrize("backend", QISKIT_RUNTIME_BACKENDS)
def test_qiskit_runtime_hamiltonian(backend, executor_class, single_job):
    """
    Check correctness of runtime executor result against normal QNode.
    """
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
    msg = (
        f"QElectron output ({val_2!r}) differs from "
        f"QNode output ({val_1!r}) by >10% (shots={SHOTS})."
    )
    assert np.isclose(val_1, val_2, rtol=0.10), msg


SINGLE_JOB_TRIPLETS = list(itertools.product([True, False], repeat=3))


@pytest.mark.parametrize("single_job_triplet", SINGLE_JOB_TRIPLETS)
def test_qiskit_runtime_hamiltonian_cluster(single_job_triplet):
    # pylint: disable=too-many-locals
    """
    Check correctness of runtime CLUSTER executor result against normal QNode.
    """
    ham_circuit, doubles, num_qubits = get_hamiltonian_circuit()

    dev = qml.device("default.qubit", wires=num_qubits, shots=SHOTS)

    # TODO: Has to be done this way for correctness. Why can't use `qml.QNode`?
    @qml.qnode(dev, diff_method="parameter-shift")
    def circuit(params):
        return ham_circuit(params)

    # Set function attribute.
    cyclic_selector.i = 0

    # Define the quantum executors cluster.
    p_1, p_2, p_3 = single_job_triplet
    qcluster = ct.executor.QCluster(
        executors=[
            ct.executor.QiskitExecutor(
                device="sampler", single_job=p_1, backend="ibmq_qasm_simulator"
            ),
            ct.executor.QiskitExecutor(
                device="sampler", single_job=p_2, backend="simulator_statevector"
            ),
            ct.executor.QiskitExecutor(device="sampler", single_job=p_3, backend="simulator_mps"),
        ],
        selector=cyclic_selector,
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
    msg = (
        f"QElectron output ({val_2!r}) differs from "
        f"QNode output ({val_1!r}) by >10% (shots={SHOTS})."
    )
    assert np.isclose(val_1, val_2, rtol=0.1), msg


TEMPLATES = [
    (qml.AngleEmbedding, (arg_vector(6),), {"wires": range(6)}),
    (qml.IQPEmbedding, (arg_vector(6),), {"wires": range(6)}),
    (qml.QAOAEmbedding, (arg_vector(6),), {"wires": range(6), "weights": weight_vector(6)}),
    (qml.DoubleExcitation, (arg_vector(4),), {"wires": range(4)}),
    (qml.SingleExcitation, (arg_vector(2),), {"wires": range(2)}),
]


@pytest.mark.parametrize("single_job", [True, False])
@pytest.mark.parametrize("executor_class", EXECUTOR_CLASSES[:1])
@pytest.mark.parametrize("template", TEMPLATES)
def test_template_circuits(template, executor_class, single_job):
    """
    Check that above Pennylane templates are working.
    """

    _template, args, kwargs = template
    num_wires = len(list(kwargs["wires"]))

    retval = _template(*args, **kwargs)

    # Define a circuit that uses the template. Also call the adjoint if allowed.
    dev = qml.device("default.qubit", wires=num_wires, shots=10_000)

    @qml.qnode(dev, interface="numpy")
    def _template_circuit():
        _template(*args, **kwargs)

        for i in range(num_wires):
            # Do this so later adjoint does not invert.
            qml.Hadamard(wires=i)

        if not isinstance(retval, qml.DoubleExcitation):
            qml.adjoint(_template)(*args, **kwargs)
        return qml.probs(wires=range(num_wires))

    qexecutor = executor_class(device="sampler", single_job=single_job)  # QiskitExecutor
    qelectron = ct.qelectron(_template_circuit, executors=qexecutor)

    val_1 = _template_circuit()
    val_2 = qelectron()

    assert isinstance(val_2, type(val_1))
    assert np.isclose(val_1, val_2, atol=0.1).all()
