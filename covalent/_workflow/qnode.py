# Copyright 2023 Agnostiq Inc.
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

"""
Define the special QNode that replaces Pennylane circuits decorated with `@ct.qelectron`.
"""

from contextlib import contextmanager
from typing import List

import pennylane as qml

from .._results_manager.qresult import QNodeFutureResult
from .._shared_files import logger
from .._shared_files.qinfo import QElectronInfo, QNodeSpecs
from .._shared_files.qresult_utils import re_execute
from .._shared_files.utils import get_original_shots
from ..executor.qbase import BaseQExecutor
from .qdevice import QEDevice

app_log = logger.app_log
log_stack_info = logger.log_stack_info

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

        # Private gradient_fn enables overriding the `gradient_fn` attribute.
        self._gradient_fn = None
        self._gradient_fn_overridden = False

        # Create a new device for every QNodeQE instance
        qe_device = QEDevice(
            wires=qnode.device.num_wires,
            shots=get_original_shots(qnode.device),
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

        future_result = QNodeFutureResult(
            batch_id,
            interface=self.device.qnode_specs.interface,
            original_qnode=self.original_qnode,
            original_tape=self.tape,
        )

        return future_result(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        Call QElectrons with args and kwargs suitable for the original QNode.
        """

        self.device.qnode_specs = self._specs(*args, **kwargs)

        # This leads to execution on the QEDevice `self.device`.
        retval = super().__call__(*args, **kwargs)
        self._update_num_executions()

        if self.device._async_run:
            # Do nothing during call from `run_later()`.
            return None

        # Skip re-execution for numpy interface.
        interface = self.device.qnode_specs.interface
        if interface in {"numpy", "autograd"}:
            return retval

        # Run through an overloaded circuit/device to loop `retval` into interfaces.
        retval = re_execute(retval, self.original_qnode, self.tape)(interface, *args, **kwargs)

        return retval

    def _update_num_executions(self):
        """
        Increment number of executions on original and custom device.
        """
        self.device._num_executions += 1
        self.original_qnode.device._num_executions += 1

    def _specs(self, *args, **kwargs) -> QNodeSpecs:
        """
        Check args and kwargs to avoid computing gradients on non-trainable parameters.
        Update the interface if it is set to "auto".
        """

        # Some args or some kwargs are trainable. No warning expected.
        if (args or kwargs) and (
            any(qml.math.get_trainable_indices(args))
            or any(qml.math.get_trainable_indices(kwargs.values()))
        ):
            specs = QNodeSpecs(**qml.specs(self)(*args, **kwargs))
        else:
            # No trainable params. Avoid warning.
            with self.override_gradient_fn(None):
                specs = QNodeSpecs(**qml.specs(self)(*args, **kwargs))

            # Replace override value with actual `gradient_fn`.
            self.construct(args, kwargs)
            specs.gradient_fn = self.gradient_fn

        # This will be done inside QNode.__call__() to update `self.interface`.
        # Here, we anticipate that change and update the specs as well.
        specs.interface = qml.math.get_interface(*args, *list(kwargs.values()))

        return specs

    @contextmanager
    def override_gradient_fn(self, fn):
        """
        Override the private `self._gradient_fn` to override the `gradient_fn`
        attribute (property).
        """
        self._gradient_fn, _tmp_gradient_fn = fn, self._gradient_fn
        self._gradient_fn_overridden = True
        try:
            yield
        finally:
            self._gradient_fn = _tmp_gradient_fn
            self._gradient_fn_overridden = False

    @property
    def gradient_fn(self):
        """
        This property replaces the `qml.QNode.gradient_fn` attribute and enables overriding it.
        """
        return self._gradient_fn

    @gradient_fn.setter
    def gradient_fn(self, fn):
        """
        Enforces gradient override.
        """
        if self._gradient_fn_overridden:
            return  # disallow setting `.gradient_fn``
        self._gradient_fn = fn
