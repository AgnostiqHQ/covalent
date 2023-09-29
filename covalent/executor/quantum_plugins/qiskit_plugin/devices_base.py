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

"""Wrappers for the existing Pennylane-Qiskit interface"""
import warnings
from abc import ABC, abstractmethod
from contextlib import contextmanager
from math import sqrt
from typing import Any, List, Sequence, Tuple, Union

import numpy as np
import pennylane.numpy as pnp
from pennylane.transforms import broadcast_expand, map_batch_transform
from pennylane_qiskit.qiskit_device import QiskitDevice
from qiskit.compiler import transpile
from sessions import init_runtime_service


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
        shots: Union[None, int, Sequence[int], Sequence[Union[int, Sequence[int]]]],
        backend_name: str,
        local_transpile: bool,
        service_init_kwargs: dict,
        **kwargs,
    ):
        # proxy for client-side `pennylane.active_return()` status
        self.pennylane_active_return = True

        super(QiskitDevice, self).__init__(wires=wires, shots=shots)

        self.shots = shots
        self.backend_name = backend_name
        self.local_transpile = local_transpile
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
    def post_process(self, *args) -> Tuple[Any, List[dict]]:
        """
        Obtain metadata; make blocking API call to Qiskit Runtime.
        """
        raise NotImplementedError

    @abstractmethod
    def post_process_all(self, *args) -> Tuple[Any, List[dict]]:
        """
        Single job version of `post_process`.
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
        shots: Union[None, int, Sequence[int], Sequence[Union[int, Sequence[int]]]],
        backend_name: str,
        local_transpile: bool,
        service_init_kwargs: dict,
        **kwargs,
    ):
        super().__init__(
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            local_transpile=local_transpile,
            service_init_kwargs=service_init_kwargs,
            **kwargs,
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

        # Used for reshaping results.
        self._n_original_circuits = None
        self._n_circuits = None

    def compile_circuits(self, circuits):
        """
        Override `QiskitDevice.compile_circuits` to include `unwrap` context.
        This step avoids potential parameter type errors during compilation.
        """
        compiled_circuits = []
        for circuit in circuits:
            # Unwraps a quantum script with tensor-like parameters to numpy arrays.
            with circuit.unwrap():
                qiskit_circuit = super().compile_circuits([circuit]).pop()
                compiled_circuits.append(qiskit_circuit)

        return compiled_circuits

    def compile(self):
        """
        Overrides `QiskitDevice.compile` with custom choice logic for the `backend`
        argument during transpilation.
        """
        backend = self.backend if self.local_transpile else None
        return transpile(self._circuit, backend=backend, **self.transpile_args)

    @property
    def asarray(self):
        """
        Array function property to return Pennylane tensors instead of NumPy arrays.
        """
        if self._asarray is np.asarray:
            return pnp.asarray
        return self._asarray

    @property
    def _state(self):
        """
        Override `self._state` to avoid unnecessary state reconstruction for
        every execution result.
        """
        if self._dummy_state is None:
            return self.dist_get_state()
        return self._dummy_state

    @property
    def vector_shape(self):
        """
        Used to reshape results in case of vector inputs.
        """
        n = self._n_original_circuits
        m = self._n_circuits // n
        return (n, m)

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
        N = 2 ** len(self.wires)

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
        dist_bin = self.normalize_probability(dist_bin)

        bit_strings = list(dist_bin)
        probs = [dist_bin[bs] for bs in bit_strings]

        # generate artificial samples from quasi-distribution probabilities
        size = self.shots if self.shots else self._default_shots
        bit_samples = np.random.choice(bit_strings, size=size, p=probs)
        return np.vstack([np.array([int(i) for i in s[::-1]]) for s in bit_samples])

    @contextmanager
    def set_distribution(self, quasi_dist):
        """
        Set the current quasi-distribution for statistics computations.
        """
        self._current_quasi_dist = quasi_dist
        try:
            yield
        finally:
            self._current_quasi_dist = None

    @staticmethod
    def normalize_probability(distribution: dict) -> dict:
        """
        Some IBMQ backends may return small NEGATIVE quasi-probabilities
        instead of ~0, when using `Sampler`.

        Below is an example of this, as observed with "ibmq_lima":

        # quasi-probabilities list
        [
            ...
            {
                "10": 0.0026338769545423205,
                "11": 0.5150691505205544,
                "00": 0.4867495783187873,
                "01": -0.004452605793883964
            },
            ...
        ]

        To avoid errors due to negative probability, this function zeros any
        negative values, then re-normalizes the quasi probabilities.
        """

        dist = distribution.copy()

        # Negative probabilities are presumed to be zero.
        delete_keys = []
        for bit_string, quasi_prob in dist.items():
            if quasi_prob <= 0:
                delete_keys.append(bit_string)

        # Zero probabilities should be omitted from the dict.
        for key in delete_keys:
            del dist[key]

        if len(dist) == 0:
            # This should never happen.
            raise RuntimeError(f"No positive probabilities exist in {distribution}.")

        # Re-normalize the remaining quasi-probabilities.
        total_prob = sum(dist.values())
        for bit_string, quasi_prob in dist.items():
            dist[bit_string] = quasi_prob / total_prob

        return dist

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
                return self.asarray(res)

            if self._shot_vector is not None:
                res = self.shot_vec_statistics(circuit)
            else:
                res = self.statistics(circuit)

        if len(circuit.measurements) > 1:
            return tuple(res)

        return self.asarray(res[0])

    def _vector_results(self, res):
        """
        Process the result of a vectorized QElectron call.
        """

        res = pnp.asarray(res)

        if self.pennylane_active_return:
            return [res] if res.ndim > 1 else list(res.reshape(self.vector_shape))

        res = res.reshape(-1)
        return [res] if res.ndim > 1 else [res.reshape(self.vector_shape)]
