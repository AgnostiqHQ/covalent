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

from contextlib import contextmanager
from typing import Any, Dict, Optional

import pennylane as qml
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ..core.device import QEDevice
from ..core.future_result import QNodeFutureResult


class QNodeSpecs(BaseModel):
    gate_sizes: Dict[str, int]
    gate_types: Dict[str, int]
    num_operations: int
    num_observables: int
    num_diagonalizing_gates: int
    num_used_wires: int
    depth: int
    num_trainable_params: int = None
    num_device_wires: int
    device_name: str
    diff_method: Optional[str]
    expansion_strategy: str
    gradient_options: Dict[str, int]
    interface: Optional[str]
    gradient_fn: Optional[str]
    num_gradient_executions: Any = 0
    num_parameter_shift_executions: int = None


class QNodeQE(qml.QNode):
    """
        Initialize a QElectron instance from a given QNode and Executor.

        Args:
            qnode (qml.QNode): The QNode to wrap.
            executors (Executor): The executors to choose from to use for running the QNode.
    """

    def __init__(self, qnode: qml.QNode, executors, qelectron_info):
        self.original_qnode = qnode

        # Create a new device for every QNodeQE instance
        qe_device = QEDevice(
            wires=qnode.device.num_wires,
            shots=qnode.device.shots,
            executors=executors,
            qelectron_info=qelectron_info,
        )

        super().__init__(
            func=qnode.func,
            device=qe_device,
            interface=qnode.interface,
            diff_method=qnode.diff_method,
            expansion_strategy=qnode.expansion_strategy,
            max_expansion=qnode.max_expansion,
        )

    @contextmanager
    def mark_call_async(self):
        # pylint: disable=protected-access
        self.device._async_run = True
        try:
            yield
        finally:
            self.device._async_run = False
            self.device._batch_id = None

    def run_later(self, *args, **kwargs):
        """
        Run the QNode asynchronously.

        Args:
            *args: Positional arguments to pass to the QNode.
            **kwargs: Keyword arguments to pass to the QNode.

        Returns:
            FutureResult: A wrapper object for the async result of running the QNode.
        """
        # pylint: disable=protected-access
        with self.mark_call_async():
            self(*args, **kwargs)
            batch_id = self.device._batch_id

        future_result = QNodeFutureResult(batch_id)

        # Required for correct output types.
        future_result.device = self.original_qnode.device
        future_result.interface = self.interface
        future_result.diff_method = self.diff_method
        future_result.qfunc_output = self.tape._qfunc_output

        return future_result

    def __call__(self, *args, **kwargs):

        self.device.qnode_specs = QNodeSpecs(**qml.specs(self)(*args, **kwargs))
        return super().__call__(*args, **kwargs)
