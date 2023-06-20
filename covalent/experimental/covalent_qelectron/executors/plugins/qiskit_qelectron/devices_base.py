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

"""Wrappers for the existing Pennylane-Qiskit interface"""
import warnings
from abc import ABC, abstractmethod
from contextlib import contextmanager
from math import sqrt
from typing import Any, List

import numpy as np
import pennylane
from pennylane.transforms import broadcast_expand, map_batch_transform
from pennylane_qiskit.qiskit_device import QiskitDevice

from .sessions import init_runtime_service


class _PennylaneQiskitDevice(QiskitDevice, ABC):
    # pylint: disable=too-many-instance-attributes
    """
    A replacement for Pennylane's `QiskitDevice` that uses `QiskitRuntimeService`
    instead of the older `qiskit.providers.provider.ProviderV1`
    """

    name = "Custom Plugin for Pennylane Circuits on Qiskit IBM Runtime"
    version = "0.0.1"
    author = "AQ"

    def __init__(
        self,
        wires: int,
        shots: int,
        backend_name: str,
        service_init_kwargs: dict,
        **kwargs
    ):
        # proxy for client-side `pennylane.active_return()` status
        self.pennylane_active_return = True

        super(QiskitDevice, self).__init__(wires=wires, shots=shots)

        self.shots = shots
        self.backend_name = backend_name
        self.service_init_kwargs = service_init_kwargs
        self.device_kwargs = kwargs

        self._service = None
        self._backend = None

        self.reset()
        self.process_kwargs(kwargs)

        self._state = None

    @classmethod
    def capabilities(cls):
        capabilities = super().capabilities().copy()
        capabilities.update(supports_broadcasting=True)
        return capabilities

    @property
    def service(self):
        """
        Lazy service property - enables serialization
        """
        if self._service is None:
            # assign cached service instance
            self._service = init_runtime_service(**self.service_init_kwargs)
        return self._service

    @property
    def backend(self):
        """
        Lazy backend property - enables serialization
        """
        if self._backend is None:
            self._backend = self.service.get_backend(self.backend_name)
        return self._backend

    def process_kwargs(self, kwargs):
        """
        Override original method from `pennylane_qiskit.qiskit_device.QiskitDevice`
        to avoid accessing backend property, unnecessary init of service
        """
        self.compile_backend = None
        self.set_transpile_args(**kwargs)
        self.run_args = kwargs.copy()

    def map_wires(self, wires):
        return wires

    def broadcast_tapes(self, tapes):
        """
        Broadcast tapes for batch execution (if necessary)
        """
        if all(tape.batch_size for tape in tapes):
            expanded_tapes, _ = map_batch_transform(broadcast_expand, tapes)
            return expanded_tapes

        return tapes

    @abstractmethod
    def post_process(self, *args) -> List[dict]:
        """
        Obtain metadata; make blocking API call to Qiskit Runtime
        """
        raise NotImplementedError


class QiskitSamplerDevice(_PennylaneQiskitDevice):

    """
    A base class for devices that use the Sampler primitive.
    """

    default_shots = 1024

    def __init__(
        self,
        wires: int,
        shots: int,
        backend_name: str,
        service_init_kwargs: dict,
        **kwargs
    ):

        super().__init__(
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            service_init_kwargs=service_init_kwargs,
            **kwargs
        )

        self._default_shots = QiskitSamplerDevice.default_shots

        if self.shots is None:
            warnings.warn(
                "The Qiskit Sampler device does not support analytic expectation values. "
                "The number of shots can not be None. "
                f"{self._default_shots} shots will be used."
            )

        self._current_quasi_dist = None
        self._dummy_state = None

    @property
    def _state(self):
        """
        Override `self._state` to avoid unnecessary state reconstruction for
        every execution result.
        """
        if self._dummy_state is None:
            return self.dist_get_state()
        return self._dummy_state

    @_state.setter
    def _state(self, state):
        """
        Allows `self._state` to be set as if instance attribute
        """
        self._dummy_state = state

    def dist_get_state(self):
        """
        Generate a state-vector from a quasi-distribution
        """
        N = 2**len(self.wires)

        state = np.zeros(N)
        for i in range(N):
            # invert bit string representation of i
            probs_idx = int(bin(i)[2:].zfill(len(self.wires))[::-1], base=2)

            if prob := self._current_quasi_dist.get(i):
                state[probs_idx] = sqrt(prob)
            else:
                state[probs_idx] = 0

        return self._asarray(state, dtype=self.C_DTYPE)

    def dist_generate_samples(self, quasi_dist):
        """
        Generate samples from a quasi-distribution
        """

        dist_bin = quasi_dist.binary_probabilities()

        bit_strings = list(dist_bin)
        probs = [dist_bin[bs] for bs in bit_strings]

        # generate artificial samples from quasi-distribution probabilities
        size = self.shots if self.shots else self._default_shots
        bit_samples = np.random.choice(bit_strings, size=size, p=probs)
        return np.vstack([np.array([int(i) for i in s[::-1]]) for s in bit_samples])

    @contextmanager
    def set_distribution(self, quasi_dist):
        self._current_quasi_dist = quasi_dist
        try:
            yield
        finally:
            self._current_quasi_dist = None

    def _process_batch_execute_result(self, circuit, quasi_dist) -> Any:
        # Update the tracker
        if self.tracker.active:
            self.tracker.update(executions=1, shots=self.shots)
            self.tracker.record()

        # Generate computational basis samples
        self._samples = self.dist_generate_samples(quasi_dist)

        with self.set_distribution(quasi_dist):

            if not self.pennylane_active_return:
                res = self._statistics_legacy(circuit)
                return self._asarray(res)
            res = self.statistics(circuit)

        if len(circuit.measurements) > 1:
            return tuple(res)

        return self._asarray(res[0])
