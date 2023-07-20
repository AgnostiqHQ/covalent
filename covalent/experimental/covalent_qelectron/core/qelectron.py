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
from typing import Optional

import pennylane
from pydantic import BaseModel

from ..core.qnode_qe import QNodeQE
from ..executors import Simulator
from ..executors.base import AsyncBaseQCluster, BaseQExecutor
from ..executors.clusters import QCluster
from ..shared_utils.utils import get_import_path


class QElectronInfo(BaseModel):
    """
    A container for QNode and Pennylane settings used by the wrapping QElectron.
    """
    name: str
    description: str = None
    qnode_device_import_path: str  # used to inherit type converters and other methods
    qnode_device_shots: Optional[int]  # optional default for execution devices
    num_device_wires: int  # this can not be reliably inferred from tapes alone
    pennylane_active_return: bool  # client-side status of `pennylane.active_return()`


def qelectron(
    qnode=None,
    *,
    executors=None,
    name=None,
    description=None,
    selector="cyclic",
):
    """
    Decorator for extending a given QNode.

    Args:
        qnode: The QNode to wrap.
        executors: The executors to choose from to use for running the QNode.
        name: The name of the QElectron. Defaults to the name of the function.
        description: A description of the QElectron. Defaults to the docstring of the function.

    Returns:
        QNodeQE: A QNodeQE instance.
    """

    if executors is None:
        executors = Simulator()

    # check if executor is a list of executors, convert to cluster if more than one
    if isinstance(executors, list):
        if not all(isinstance(ex, BaseQExecutor) for ex in executors):
            raise ValueError("Invalid executor in executors list.")
        if len(executors) > 1:
            executors = QCluster(executors=executors, selector=selector)

    # check if executor is a QCluster and serialize the selector
    if isinstance(executors, AsyncBaseQCluster):
        executors.serialize_selector()

    # check if executor is a list of executors
    if not isinstance(executors, list):
        executors = [executors]

    if qnode is None:
        return functools.partial(qelectron, executors=executors, name=name, description=description)

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
        pennylane_active_return=pennylane.active_return(),
    )

    # Create a new QNodeQE instance for every qelectron call
    return QNodeQE(qnode, executors, qelectron_info)
