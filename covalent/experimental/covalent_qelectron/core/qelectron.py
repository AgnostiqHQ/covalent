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

import functools
from typing import Callable, List, Optional, Union

import pennylane as qml

from ..core.qnode_qe import QElectronInfo, QNodeQE
from ..executors import Simulator
from ..executors.base import AsyncBaseQCluster, BaseQExecutor
from ..executors.clusters import QCluster
from ..shared_utils.utils import get_import_path

Selector = Union[str, Callable[[qml.tape.QuantumScript, List[BaseQExecutor]], BaseQExecutor]]


def qelectron(
    qnode: qml.QNode = None,
    *,
    executors: Union[BaseQExecutor, AsyncBaseQCluster, List[BaseQExecutor]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    selector: Union[str, Selector] = "cyclic",
) -> QNodeQE:
    """
    QElectron decorator to be called upon a Pennylane QNode. Enables parallelized,
    asynchronous execution of circuits on one or more quantum backends, as specified
    by the `executors` argument.

    Args:
        qnode: The Pennylane QNode to wrap.

    Keyword Args:
        executors: The quantum executor(s) to use for running the QNode. A single
            executor, list of executors, or a `QCluster` instance are accepted.
            If a list of multiple executors is passed, a quantum cluster will be
            initialized from this list automatically, using `selector` as the
            cluster's selector. Defaults to a `Simulator` instance if not specified.
        name: An optional name for the QElectron. Defaults to name of the circuit
            function.
        description: An optional description of the QElectron. Defaults to the
            circuit function's docstring.
        selector: A callable that selects an executor. The strings "cyclic" and
            "random" are also accepted. The default "cyclic" selector returns
            elements of `executors` in order, restarting from the first element
            upon reaching the last. The "random" selector chooses from `executors`
            at random, for each circuit. Any user-defined selector must be callable
            with two arguments (a circuit and a list of executors), and must always
            return only one executor.

    Raises:
        ValueError: If any invalid executors are passed.

    Returns:
        `QNodeQE`: A sub-type of QNode that integrates QElectrons.
    """

    if executors is None:
        executors = Simulator()

    # Check if executor is a list of executors.
    if isinstance(executors, list):
        if not all(isinstance(ex, BaseQExecutor) for ex in executors):
            raise ValueError("Invalid executor in executors list.")
        if len(executors) > 1:
            # Convert to cluster if more than one executor in list.
            executors = QCluster(executors=executors, selector=selector)

    # Check if executor is a QCluster.
    if isinstance(executors, AsyncBaseQCluster):
        # Serialize the cluster's selector function.
        executors.serialize_selector()

    # Check if a single executor instance was passed.
    if not isinstance(executors, list):
        executors = [executors]

    if qnode is None:
        # This only happens when `qelectron()` is not used as a decorator.
        return functools.partial(
            qelectron,
            executors=executors,
            name=name,
            description=description
        )

    # Set default name and description.
    if name is None:
        name = qnode.func.__name__

    if description is None:
        description = qnode.func.__doc__

    qelectron_info = QElectronInfo(
        name=name,
        description=description,
        qnode_device_import_path=get_import_path(type(qnode.device)),
        qnode_device_shots=qnode.device.shots,
        num_device_wires=qnode.device.num_wires,
        pennylane_active_return=qml.active_return(),
    )

    # Create and return a new `QNodeQE` instance.
    return QNodeQE(qnode, executors, qelectron_info)
