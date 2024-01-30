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

import numpy as np
import pennylane as qml
import pytest

import covalent as ct
from covalent._shared_files.config import get_config

from ..utils import arg_vector, simple_circuit, weight_vector

EXECUTOR_CLASSES = [
    ct.executor.QiskitExecutor,
    ct.executor.IBMQExecutor,
]


@pytest.mark.parametrize("executor_class", EXECUTOR_CLASSES)
def test_defaults_copied_from_config(executor_class):
    """
    Check that instances get default values from the covalent config file.
    """

    # Initialize a minimal executor.
    qexecutor = executor_class(device="local_sampler")

    # Get executor as a dictionary.
    exec_config = qexecutor.dict()

    # Retrieve default values from config file.
    name = executor_class.__name__
    default_config = get_config("qelectron")[name]

    # Test equivalence.
    if hasattr(qexecutor, "options"):
        config_without_options = default_config.copy()
        config_options = config_without_options.pop("options")

        for k, val in config_without_options.items():
            assert exec_config[k] == val

        for k, val in config_options.items():
            exec_options = dict(exec_config["options"])
            assert exec_options[k] == val
    else:
        for k, val in default_config.items():
            assert exec_config[k] == val


def test_qiskit_exec_shots_is_none():
    """
    Check that a warning is raised if shots is None.
    """

    dev = qml.device("default.qubit", wires=2, shots=None)
    qnode = qml.QNode(simple_circuit, device=dev)

    qexecutor = ct.executor.QiskitExecutor(device="local_sampler", shots=None)
    qelectron = ct.qelectron(qnode, executors=qexecutor)

    val_1 = qnode(0.5)
    with pytest.warns(UserWarning, match="The number of shots can not be None."):
        val_2 = qelectron(0.5)

    assert isinstance(val_2, type(val_1))


def test_default_return_type():
    """
    Test that a QElectron with the default QNode interface returns the correct type.
    """

    executor = ct.executor.QiskitExecutor(device="local_sampler", shots=1024)

    dev = qml.device("default.qubit", wires=2)

    # QElectron definition.
    @ct.qelectron(executors=executor)
    @qml.qnode(device=dev)
    def qelectron_circuit(param):
        qml.RX(param, wires=0)
        qml.Hadamard(wires=1)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.operation.Tensor(*(qml.PauliY(0), qml.PauliX(1))))

    # Equivalent QNode definition (for comparison).
    @qml.qnode(device=dev)
    def normal_circuit(param):
        qml.RX(param, wires=0)
        qml.Hadamard(wires=1)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.operation.Tensor(*(qml.PauliY(0), qml.PauliX(1))))

    res = normal_circuit(0.5)
    qres = qelectron_circuit(0.5)

    assert isinstance(qres, type(res)), f"Results {res!r} and {qres!r} are not the same type"


_TEMPLATES = [
    (qml.AngleEmbedding, (arg_vector(6),), {"wires": range(6)}),
    (qml.IQPEmbedding, (arg_vector(6),), {"wires": range(6)}),
    (qml.QAOAEmbedding, (arg_vector(6),), {"wires": range(6), "weights": weight_vector(6)}),
    (qml.DoubleExcitation, (arg_vector(4),), {"wires": range(4)}),
    (qml.SingleExcitation, (arg_vector(2),), {"wires": range(2)}),
]


@pytest.mark.parametrize("executor_class", EXECUTOR_CLASSES[:1])
@pytest.mark.parametrize("template", _TEMPLATES)
def test_template_circuits(template, executor_class):
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

    qexecutor = executor_class(device="local_sampler")  # QiskitExecutor
    qelectron = ct.qelectron(_template_circuit, executors=qexecutor)

    val_1 = _template_circuit()
    val_2 = qelectron()

    assert isinstance(val_2, type(val_1))
    assert np.isclose(val_1, val_2, atol=0.1).all()
