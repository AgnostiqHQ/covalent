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

from typing import Any

import pennylane as qml
from pennylane.tape import QuantumTape

from ..middleware.core import middleware


class QNodeFutureResult:
    """
    A class that stores the `batch_id` of a batch of circuits submitted to the
    middleware. The `result` method can then be called to retrieve the results.

    Attributes:
        device: The Pennylane device used by the original QNode.
        interface: The interface of the original QNode.
        diff_method: The differentiation method of the original QNode.
        qfunc_output: The return value (measurement definition) of the original QNode.
    """

    def __init__(
        self,
        batch_id: str,
        original_qnode: qml.QNode,
        original_tape: QuantumTape,
    ):
        """
        Initialize a `QNodeFutureResult` instance.

        Args:
            batch_id: A UUID that identifies a batch of circuits submitted to
                the middleware.
        """
        self.batch_id = batch_id

        # Required for batch_transforms and correct output typing.
        self.device = original_qnode.device
        self.interface = original_qnode.interface
        self.diff_method = original_qnode.diff_method
        self.tape = original_tape

        self._result = None

    def result(self) -> Any:
        """
        Retrieve the results for the given `batch_id` from middleware. This method
        is blocking until the results are available.

        Returns:
            The results of the circuit execution.
        """

        if self._result is None:

            # Get raw results from the middleware.
            results = middleware.get_results(self.batch_id)

            # Create a device from the original QNode's device class for correct typing.
            dev = _run_later_device_factory(results, self.device, self.tape)

            # Define a dummy circuit that returns the original QNode's return value.
            @qml.qnode(dev, interface=self.interface, diff_method=self.diff_method)
            def _dummy_circuit():
                return self.tape._qfunc_output  # pylint: disable=protected-access

            self._result = _dummy_circuit()

        return self._result


def _run_later_device_factory(
    results: Any,
    original_device: qml.Device,
    original_tape: QuantumTape,
) -> qml.Device:
    """
    Returns an instance of a new class that inherits from the original QNode's
    device class. Inheriting ensures the correct return type, while overriding
    `batch_execute` returns the expected `results` without actually running circuits.
    """

    qml_device_cls = type(original_device)

    class _RunLaterDevice(qml_device_cls):
        # pylint: disable=too-few-public-methods

        def batch_execute(self, circuits):
            """
            Override to return expected result.
            """
            n_circuits = len(circuits)

            if n_circuits > 1 or len(results) > 1:
                return [results] * n_circuits
            return results

        def batch_transform(self, _):
            """
            Ignore blank circuit and run batch transform on original tape.
            """
            return original_device.batch_transform(original_tape)

    wires = original_device.num_wires
    return _RunLaterDevice(wires=wires, shots=1)
