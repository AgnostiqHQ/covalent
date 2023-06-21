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

"""
Configuration that enables easy adoption of Pennylane tests to QElectrons.

NOTE: ONLY USE this configuration file with Pennylane tests.
"""
import inspect
from unittest.mock import patch

import pennylane as qml
import pytest

import covalent as ct
from covalent.experimental import covalent_qelectron as cq

SKIP_RETURN_TYPES = [
    "qml.apply",
    "qml.vn_entropy",
    "qml.mutual_info"
]

SKIP_DEVICES = [
    "default.qutrit",
    "default.mixed",
]

XFAIL_TEST_NAMES = [
    "test_array_multiple"  # NOTE: produces array with inhomogeneous shape
]


def _check_return_type(func):
    """
    Checks whether a function returns a type that is not supported by QElectrons.
    """

    func_lines = inspect.getsourcelines(func)[0]
    reached_return = False
    for line in func_lines:

        if line.strip().startswith("return"):
            reached_return = True

        if reached_return:
            for ret_typ in SKIP_RETURN_TYPES:
                if ret_typ in line or ret_typ.split(".", maxsplit=1)[-1] in line:
                    pytest.skip(f"QElectrons don't support `{ret_typ}` measurements.")


def _check_device_type(device):
    """
    Checks whether a device is supported by QElectrons.
    """

    if device.short_name in SKIP_DEVICES:
        pytest.skip(f"QElectrons don't support the `{device}` device.")
    if device.shot_vector:
        pytest.skip("QElectrons don't support shot vectors.")


def get_wrapped_QNode(cls, use_run_later=False):  # pylint: disable=invalid-name
    """
    Patches `qml.QNode` to return a QElectron instead.
    """

    class _PatchedQNode(cls):
        # pylint: disable=too-few-public-methods

        """
        This class replaces `qml.QNode`
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._init_qelectron(*args, **kwargs)

        def _init_qelectron(self, *args, **kwargs):
            func, device = args
            _check_return_type(func)
            _check_device_type(device)

            qnode = cls(func, device, **kwargs)

            # QElectron that wraps the normal QNode
            self.qelectron = cq.qelectron(
                qnode=qnode,
                executors=ct.executor.QiskitExecutor(  # pylint: disable=no-member
                    device="local_sampler",
                    shots=qnode.device.shots,
                )
            )

        def __call__(self, *args, **kwargs):
            if use_run_later:
                return self.qelectron.run_later(*args, **kwargs).result()
            return self.qelectron(*args, **kwargs)

    return _PatchedQNode


@pytest.fixture(autouse=True)
def patch_qnode_creation():
    """
    Wraps the `pennylane.QNode` class such that the `qml.qnode()` decorator
    instead creates QElectrons that wrap a QNode.
    """
    with patch("pennylane.QNode", new=get_wrapped_QNode(qml.QNode, use_run_later=False)):
        yield


def pytest_collection_modifyitems(config, items):  # pylint: disable=unused-argument
    """
    Using Pytest hook to xfail selected tests.
    """
    for item in items:
        if any(name in item.nodeid for name in XFAIL_TEST_NAMES):
            item.add_marker(
                pytest.mark.xfail(reason="XFailing test also failed by normal QNode.")
            )
