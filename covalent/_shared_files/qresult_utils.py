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

import warnings
from typing import Any, Callable, List, Optional

import pennylane as qml
from pennylane import transforms
from pennylane.measurements import ExpectationMP
from pennylane.tape import QuantumTape

from .._workflow.qdevice import QEDevice
from .utils import get_original_shots


def re_execute(
    results: Any,
    qnode: qml.QNode,
    tape: QuantumTape,
) -> Callable:
    """
    Send the QElectron QNode's result through a "shell" QNode to achieve correct typing
    and shape transformations.

    This is necessary because the QEDevice can not support 'passthru_devices' in
    its capabilities, since that would circumvent its custom `batch_execute` method.
    """

    def re_execute_wrapper(interface, *args, **kwargs):
        circuit = shell_circuit_factory(results, qnode, tape, interface)
        return circuit(*args, **kwargs)

    return re_execute_wrapper


def shell_circuit_factory(
    results: Any,
    qnode: qml.QNode,
    tape: QuantumTape,
    interface: Optional[str],
) -> qml.QNode:
    """
    Returns a circuit that does nothing but transform and return the results.
    """

    dev = shell_device_factory(results, qnode, tape, interface)

    # Define a dummy circuit that returns the original QNode's return value.
    @qml.qnode(dev, interface=qnode.interface, diff_method=qnode.diff_method)
    def _circuit(*_, **__):
        return tape._qfunc_output  # pylint: disable=protected-access

    return _circuit


def shell_device_factory(
    results: Any,
    qnode: qml.QNode,
    original_tape: QuantumTape,
    interface: Optional[str],
) -> qml.Device:
    """
    Returns an instance of a new class that inherits from the original QNode's device class.
    """

    default_capabilities = QEDevice.capabilities().copy()

    # Conditional override of the device's capabilities to accommodate interface.
    overriden_capabilities = _override_capabilities(results, interface, default_capabilities)

    class _ShellDevice(qnode.device.__class__):
        # pylint: disable=too-few-public-methods

        def batch_execute(self, circuits):
            """
            Override to return expected result.
            """
            return _reshape_for_interface(interface, circuits, results)

        def batch_transform(self, tape):
            """
            Ignore blank circuit and run batch transform on original tape.
            """

            # Conditional lifted from `qml.transforms.hamiltonian_expand`.
            if not (
                len(original_tape.measurements) != 1
                or not isinstance(original_tape.measurements[0].obs, qml.Hamiltonian)
                or not isinstance(original_tape.measurements[0], ExpectationMP)
            ):
                # Apply batch transform for Hamiltonian expvals.
                return transforms.hamiltonian_expand(original_tape)

            if original_tape.output_dim > 1:
                res = results if hasattr(results, "__len__") else [[r] for r in results]
                return [tape], lambda _, **kw: res

            # Apply identity transform.
            return [tape], lambda _, **kw: results

        @classmethod
        def capabilities(cls):
            """
            Copy the QElectron Device capabilities to avoid passthru devices and
            overload using `diff_method="backprop` and associated transform with
            default settings.
            """
            if overriden_capabilities is None:
                return QEDevice.capabilities().copy()
            return overriden_capabilities.copy()

    # Recreate device with original number of wires.
    dev = _ShellDevice(wires=qnode.device.num_wires, shots=1)

    # Use the `shots` property setter on `qml.Device` to set the shots or shot vector.
    dev.shots = get_original_shots(qnode.device)  # pylint: disable=attribute-defined-outside-init

    return dev


def _override_capabilities(
    results: Any, interface: str, default_capabilities: dict
) -> Optional[dict]:
    """
    Implements interface-based conditional overrides for device capabilities.
    """
    if interface in {None, "auto", "numpy", "autograd"}:
        # No override necessary.
        return default_capabilities

    # Require passthrough for some interfaces.
    if interface == "torch":
        if isinstance(results, list) or results.ndim == 0:
            return {
                "model": "qubit",
                "passthru_interface": "torch",
            }
        return default_capabilities

    if interface == "jax":
        return {
            "model": "qubit",
            "passthru_interface": "jax",
        }

    warnings.warn(f"Skipped capabilities override. No logic defined for '{interface}' interface")
    return default_capabilities


def _reshape_for_interface(interface: str, circuits: List[QuantumTape], results: Any):
    """
    Reshape or re-package the return value in an interface-specific way to satisfy
    expected shape or type requirements in Pennylane's execution pipeline.
    """

    if interface in {"auto", "numpy"}:
        # More than one circuit and more than one result.
        if len(circuits) > 1 and hasattr(results, "__len__") and len(results) > 1:
            return [[r] for r in results]

        # Results is a 0-dimensional array.
        if hasattr(results, "ndim") and results.ndim == 0:
            return [results]

        # No reshaping required.
        return results

    if interface in {None, "autograd", "torch", "jax"}:
        # Ensure result is a list.
        if isinstance(results, list):
            return results
        return [results]

    warnings.warn(f"Skipped reshaping result. No logic defined for '{interface}' interface")
    return results
