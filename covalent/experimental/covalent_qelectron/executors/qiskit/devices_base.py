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
from abc import ABC, abstractmethod
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

    def dist_generate_samples(self, quasi_dist):
        """
        Generate samples from a quasi-distribution
        """

        dist_bin = quasi_dist.binary_probabilities()

        bit_strings = list(dist_bin)
        probs = [dist_bin[bs] for bs in bit_strings]

        # generate artificial samples from quasi-distribution probabilities
        bit_samples = np.random.choice(bit_strings, size=self.shots, p=probs)
        return np.vstack([np.array([int(i) for i in s[::-1]]) for s in bit_samples])

    def _process_batch_execute_result(self, circuit, quasi_dist) -> Any:
        # Update the tracker
        if self.tracker.active:
            self.tracker.update(executions=1, shots=self.shots)
            self.tracker.record()

        # Generate computational basis samples
        if self.shots is not None or circuit.is_sampled:
            self._samples = self.dist_generate_samples(quasi_dist)

        # Adjust for active return status
        if not pennylane.active_return():
            res = self._statistics_legacy(circuit)
            return np.asarray(res)

        res = self.statistics(circuit)
        single_measurement = len(circuit.measurements) == 1
        res = res[0] if single_measurement else tuple(res)

        return pennylane.numpy.asarray(res)
