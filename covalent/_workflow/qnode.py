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
from typing import Any, Dict, List, Optional

import pennylane as qml
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .._results_manager.qresult import QNodeFutureResult
from ..executor.qbase import BaseQExecutor
from .qdevice import QEDevice


class QNodeSpecs(BaseModel):
    """
    A container for the specifications of a QNode.
    """
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


class QElectronInfo(BaseModel):
    """
    A container for related settings used by the wrapping QElectron.
    """
    name: str
    description: str = None
    qnode_device_name: str  # name of the original device, e.g. "default.qubit"
    qnode_device_import_path: str  # used to inherit type converters and other methods
    qnode_device_shots: Optional[int]  # optional default for execution devices
    num_device_wires: int  # this can not be reliably inferred from tapes alone
    pennylane_active_return: bool  # client-side status of `pennylane.active_return()`


_GRADIENT_ACCESS_MAXES = {
    "parameter-shift": 2,
}


class QNodeQE(qml.QNode):
    """
    A sub-type of Pennylane's QNode that integrates Covalent QElectrons.

    Attributes:
        original_qnode: The original QNode that was wrapped.
        device: The `QEDevice` instance used for circuit execution instead of the
            original QNode's device.
    """

    def __init__(
        self,
        qnode: qml.QNode,
        executors: List[BaseQExecutor],
        qelectron_info: QElectronInfo,
    ):
        """
        Initialize a `QNodeQE` instance.

        Args:
            qnode: The Pennylane QNode replaced by this object.
            executors: A list of executors to use for circuit execution.
            qelectron_info: Settings related to the original QNode.
        """

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

        self._gradient_fn = None
        self._override_gradient_fn = None
        self._gradient_access_counter = 0

        # Update `execute_kwargs` such that `qe_device.batch_execute` will be called
        # to obtain the circuits result, and `qe_device.gradients` will be called
        # to obtain the gradients.
        if self.device.qelectron_info.pennylane_active_return:
            self.execute_kwargs.update(grad_on_execution=False)
        else:
            self.execute_kwargs.update(mode="backward")

    @contextmanager
    def mark_call_async(self):
        """
        Activates async execution mode for this instance.
        """
        # pylint: disable=protected-access
        self.device._async_run = True
        try:
            yield
        finally:
            self.device._async_run = False
            self.device._batch_id = None

    def run_later(self, *args, **kwargs) -> QNodeFutureResult:
        """
        Calls this QNode asynchronously. This method returns immediately, without
        waiting for the circuit to finish executing.

        Returns:
            future_result: An object that can be queried for the execution result.
        """

        # pylint: disable=protected-access
        with self.mark_call_async():
            self(*args, **kwargs)
            batch_id = self.device._batch_id

        return QNodeFutureResult(batch_id, self.original_qnode, self.tape)

    def __call__(self, *args, **kwargs):

        self.device.qnode_specs = self._specs(*args, **kwargs)
        with self.override_gradient_fn("device"):
            return super().__call__(*args, **kwargs)

    def _specs(self, *args, **kwargs) -> QNodeSpecs:
        """
        Check args and kwargs to avoid computing gradients on non-trainable parameters.
        """

        # No args or kwargs to worry about.
        if not args and not kwargs:
            return QNodeSpecs(**qml.specs(self)(*args, **kwargs))

        # Some args or some kwargs are trainable. No warning expected.
        if (
            any(qml.math.get_trainable_indices(args)) or any(qml.math.get_trainable_indices(kwargs.values()))
        ):
            return QNodeSpecs(**qml.specs(self)(*args, **kwargs))

        # No trainable params. Avoid warning.
        with self.override_gradient_fn("none"):
            return QNodeSpecs(**qml.specs(self)(*args, **kwargs))

    @contextmanager
    def override_gradient_fn(self, gradient_fn):
        """
        Set the `_override_gradient_fn` attribute to enable custom `gradient_fn`
        property behavior.
        """
        self._override_gradient_fn = gradient_fn
        try:
            yield
        finally:
            self._override_gradient_fn = None

    @property
    def gradient_access_max(self):
        """
        Return the maximum number of times the `gradient_fn` property can be
        accessed before the overridden value is returned and the counter is reset.
        """
        return _GRADIENT_ACCESS_MAXES.get(self.diff_method, -1)

    @property
    def gradient_fn(self):
        """
        Override the `gradient_fn` attribute to return custom value (as set by
        `override_gradient_fn`) every second time the property is accessed.
        """
        if (
            self._override_gradient_fn and self._gradient_access_counter >= self.gradient_access_max
        ):
            self.reset_gradient_counter()
            return self._override_gradient_fn

        # Increment access counter.
        self._gradient_access_counter += 1
        return self._gradient_fn

    @gradient_fn.setter
    def gradient_fn(self, fn):
        # Set attribute and reset access counter.
        self._gradient_fn = fn
        self.reset_gradient_counter()

    def reset_gradient_counter(self):
        """
        Reset the gradient access counter to 0.
        """
        self._gradient_access_counter = 0
