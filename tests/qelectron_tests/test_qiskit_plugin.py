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

import covalent as ct
from covalent._shared_files.config import get_config

from .utils import simple_circuit

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
            assert getattr(exec_config["options"], k) == val
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
