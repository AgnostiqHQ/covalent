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

from .utils import get_original_shots


def re_execute(
    args, kwargs,
    *,
    results: Any,
    qnode: qml.QNode,
    tape: QuantumTape,
):
    """
    Send the QElectron QNode's result through a "shell" QNode to achieve correct typing
    and shape transformations.

    This is necessary because the QEDevice can not support 'passthru_devices' in
    its capabilities, since that would circumvent its custom `batch_execute` method.
    """

    # Create a device from the original QNode's device class for correct typing.
    dev = shell_device_factory(results, qnode, tape)

    # Define a dummy circuit that returns the original QNode's return value.
    @qml.qnode(dev, interface=qnode.interface, diff_method=qnode.diff_method)
    def _circuit(*_, **__):
        return tape._qfunc_output  # pylint: disable=protected-access

    return _circuit(*args, **kwargs)


def shell_device_factory(
    results: Any,
    qnode: qml.QNode,
    tape: QuantumTape,
) -> qml.Device:
    """
    Returns an instance of a new class that inherits from the original QNode's
    device class. Inheriting ensures the correct return type, while overriding
    `batch_execute` returns the expected `results` without actually running circuits.
    """

    class _ShellDevice(qnode.device.__class__):
        # pylint: disable=too-few-public-methods

        def batch_execute(self, circuits):
            """
            Override to return expected result.
            """
            if len(circuits) > 1 or len(results) > 1:
                return [[r] for r in results]
            return results

        def batch_transform(self, _):
            """
            Ignore blank circuit and run batch transform on original tape.
            """
            return qnode.device.batch_transform(tape)

    dev = _ShellDevice(wires=qnode.device.num_wires, shots=1)

    # Use the `shots` property setter on `qml.Device` to set the shots or shot vector.
    dev.shots = get_original_shots(qnode.device)

    return dev
