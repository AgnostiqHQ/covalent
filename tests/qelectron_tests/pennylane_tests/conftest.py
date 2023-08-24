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
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

"""
Configuration that enables easy adoption of Pennylane tests to QElectrons.

NOTE: ONLY USE this configuration file with Pennylane tests.
"""
import inspect
import random
from unittest.mock import patch

import pennylane as qml
import pytest

import covalent as ct

SKIP_RETURN_TYPES = ["qml.apply", "qml.vn_entropy", "qml.mutual_info"]

SKIP_DEVICES = [
    "default.qutrit",
    "default.mixed",
]

XFAIL_TEST_NAMES = ["test_array_multiple"]  # NOTE: produces array with inhomogeneous shape


# VALIDATION FUNCTIONS
# ------------------------------------------------------------------------------


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


# UTILITIES
# ------------------------------------------------------------------------------


def _init_Simulator(shots):
    return ct.executor.Simulator(parallel="thread", shots=shots)


def _init_Simulator_cluster(shots):
    return [
        ct.executor.Simulator(parallel="thread", shots=shots),
        ct.executor.Simulator(parallel="thread", shots=shots),
    ]


def _init_QiskitExecutor_local_sampler(shots):
    return ct.executor.QiskitExecutor(
        device="local_sampler",
        shots=shots,
    )


def _init_QiskitExecutor_local_sampler_cluster(shots):
    return [
        ct.executor.QiskitExecutor(
            device="local_sampler",
            shots=shots,
        ),
        ct.executor.QiskitExecutor(
            device="local_sampler",
            shots=shots,
        ),
    ]


def _init_LocalBraketQubitExecutor(shots):
    return ct.executor.LocalBraketQubitExecutor(shots=shots)


def _init_LocalBraketQubitExecutor_cluster(shots):
    return [
        ct.executor.LocalBraketQubitExecutor(shots=shots),
        ct.executor.LocalBraketQubitExecutor(shots=shots),
    ]


def _get_wrapped_QNode(use_run_later, get_executors):  # pylint: disable=invalid-name
    """
    Patches `qml.QNode` to return a QElectron instead.
    """

    class _PatchedQNode(qml.QNode):
        # pylint: disable=too-few-public-methods

        """
        This class replaces `qml.QNode`
        """

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            qnode = self
            _check_return_type(qnode.func)
            _check_device_type(qnode.device)

            # QElectron that wraps the normal QNode
            self.qelectron = ct.qelectron(
                qnode=qnode, executors=get_executors(shots=qnode.device.shots)
            )

        def __call__(self, *args, **kwargs):
            if use_run_later:
                return self.qelectron.run_later(*args, **kwargs).result()
            return self.qelectron(*args, **kwargs)

    return _PatchedQNode


# HOOKS
# ------------------------------------------------------------------------------


def pytest_collection_modifyitems(config, items):  # pylint: disable=unused-argument
    """
    Using Pytest hook to xfail selected tests.
    """
    for item in items:
        if any(name in item.nodeid for name in XFAIL_TEST_NAMES):
            item.add_marker(pytest.mark.xfail(reason="XFailing test also failed by normal QNode."))


# FIXTURES
# ------------------------------------------------------------------------------


@pytest.fixture(params=[True, False])
def use_run_later(request):
    """
    Determines whether QElectron is called normally or through `run_later`.
    """
    return request.param


QEXECUTORS = [
    _init_Simulator,
    _init_Simulator_cluster,
    _init_QiskitExecutor_local_sampler,
    _init_QiskitExecutor_local_sampler_cluster,
    _init_LocalBraketQubitExecutor,
    _init_LocalBraketQubitExecutor_cluster,
]


@pytest.fixture(params=QEXECUTORS)
def get_executors(request):
    """
    Determines the QExecutor that is used.
    """
    return request.param


@pytest.fixture(autouse=True)
def patch_qnode_creation(use_run_later, get_executors):
    """
    Wraps the `pennylane.QNode` class such that the `qml.qnode()` decorator
    instead creates QElectrons that wrap a QNode.
    """
    patched_cls = _get_wrapped_QNode(use_run_later, get_executors)
    with patch("pennylane.QNode", new=patched_cls):
        yield
