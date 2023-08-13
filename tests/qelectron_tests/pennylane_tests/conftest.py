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
from typing import List
from unittest.mock import patch

import pennylane as qml
import pytest

import covalent as ct
from covalent._shared_files.utils import get_original_shots
from covalent.quantum.qcluster.simulator import SIMULATOR_DEVICES

SKIP_RETURN_TYPES = [
    "qml.apply",
    "qml.vn_entropy",
    "qml.mutual_info"
]

SKIP_DEVICES = [
    "default.qutrit",
    "default.mixed",
    "default.gaussian",  # TODO: allow for Simulator
]

# XFAIL NOTES LEGEND
# (1) configuration issue; test passes manually
# (2) incompatible; requires manual test
# -----------------
XFAIL_TEST_NAMES = [
    # "test_array_multiple"  # NOTE: produces array with inhomogeneous shape

    # Case 0 #
    # fails and support not planned
    "test_qutrit_device::test_device_executions",

    # Case 1 #
    # configuration issue, test passes manually
    "test_qaoa::test_partial_cycle_mixer",
    "test_qaoa::test_self_loop_raises_error",
    "test_qaoa::test_inner_out_flow_constraint_hamiltonian_non_complete",
    "test_qaoa::test_inner_net_flow_constraint_hamiltonian_non_complete",

    # Case 2 #
    # incompatible test, needs manual equivalent
    "test_qnode::test_diff_method",
    "test_qnode::test_jacobian",
]


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


def _check_device_type(executors, device):
    """
    Checks whether a device is supported by QElectrons.
    """

    if not isinstance(executors, list):
        # Always handle as list.
        executors = [executors]

    if device.short_name in SKIP_DEVICES:
        simulator_in_execs = any(isinstance(ex, ct.executor.Simulator) for ex in executors)
        if not (simulator_in_execs and device.short_name == "default.gaussian"):
            pytest.skip(f"QElectrons do not support the '{device.short_name}' device.")
    # if device.shot_vector:
    #     pytest.skip("QElectrons don't support shot vectors.")


    # Simulator
    if any(isinstance(ex, ct.executor.Simulator) for ex in executors):
        if device.short_name not in SIMULATOR_DEVICES:
            pytest.skip(f"Simulator does not support the '{device.short_name}' device.")


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


# QNODE PATCH THAT SUBSTITUTES IN QELECTRON
# ------------------------------------------------------------------------------

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

            shots = get_original_shots(self.device)
            executors = get_executors(shots)
            qnode = self
            shots = get_original_shots(qnode.device)
            executors = get_executors(shots=shots)

            _check_return_type(executors, qnode.func)
            _check_device_type(executors, qnode.device)

            # QElectron that wraps the normal QNode
            self.qelectron = ct.qelectron(
                qnode=qnode,
                executors=get_executors(shots=get_original_shots(self.device))
            )

        def __call__(self, *args, **kwargs):
            if use_run_later:
                return self.qelectron.run_later(*args, **kwargs).result()
            return self.qelectron(*args, **kwargs)

    return _PatchedQNode


# VALIDATION FUNCTIONS
# ------------------------------------------------------------------------------

def _check_return_type(executors, func):
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


def _check_device_type(executors, device):
    """
    Checks whether a device is supported by QElectrons.
    """

    if device.short_name in SKIP_DEVICES:
        pytest.skip(f"QElectrons don't support the `{device}` device.")
    if device.shot_vector:
        if (
            isinstance(executors, ct.executor.LocalBraketQubitExecutor) or
            any(isinstance(ex, ct.executor.LocalBraketQubitExecutor) for ex in executors)
        ):
            pytest.skip("Braket executor does not support shot vectors")


# SKIP SETTINGS
# ------------------------------------------------------------------------------

SKIP_RETURN_TYPES = [
    "qml.apply",
    "qml.vn_entropy",
    "qml.mutual_info"
]

SKIP_DEVICES = [
    "default.qutrit",
    "default.mixed",
]

SKIP_FOR_RUN_LATER = [
    # NOTE: calls qml.jacobian(qe_circuit.run_later(input).result())
    "test_numerical_analytic_diff_agree",
]

XFAIL_TEST_NAMES = [
    "test_array_multiple"  # NOTE: produces array with inhomogeneous shape
]

XFAIL_TEST_NAMES_CONDITIONAL = {

    # NOTE: mocker.spy(qml.QubitDevice, "probability") working incorrectly for Braket executor.
    "test_numerical_analytic_diff_agree": lambda item: (
        item.callspec.params.get('get_executors') is _init_LocalBraketQubitExecutor or
        item.callspec.params.get('get_executors') is _init_LocalBraketQubitExecutor_cluster
    ),

}


# TEST UTILITIES
# ------------------------------------------------------------------------------

def _get_test_name(nodeid: str):
    """
    Returns the name of a test.
    """
    return nodeid.split("::")[-1].split("[")[0]


# HOOKS
# ------------------------------------------------------------------------------

def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):  # pylint: disable=unused-argument
    """
    Using Pytest hook to xfail selected tests.
    """
    for item in items:

        # XFail tests expected to fail in general.
        if any(name in item.nodeid for name in XFAIL_TEST_NAMES):
            item.add_marker(
                pytest.mark.xfail(reason="XFailing test also failed by normal QNode.")
            )

        # XFail tests expected to fail with `QElectron.run_later`
        if 'use_run_later' in item.fixturenames and item.callspec.params.get('use_run_later'):
            if any(name in item.nodeid for name in SKIP_FOR_RUN_LATER):
                item.add_marker(
                    pytest.mark.skip(
                        reason=f"{item.nodeid} expected to fail with `QElectron.run_later`")
                )

        # XFail tests expected to fail in certain conditions.
        if any(name in item.nodeid for name in XFAIL_TEST_NAMES_CONDITIONAL):
            condition = XFAIL_TEST_NAMES_CONDITIONAL[_get_test_name(item.nodeid)]
            if condition(item):
                item.add_marker(
                    pytest.mark.xfail(reason="XFailing test also failed by normal QNode.")
                )


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
