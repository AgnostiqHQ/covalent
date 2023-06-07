"""Wrappers for the existing Pennylane-Qiskit interface"""
from abc import abstractmethod
from typing import Any, List, Tuple

import numpy as np
import pennylane
from pennylane.transforms import broadcast_expand, map_batch_transform
from pennylane_qiskit.qiskit_device import QiskitDevice
from qiskit.compiler import transpile

from .sessions import init_runtime_service


class _PennylaneQiskitDevice(QiskitDevice):
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

    def broadcast_tapes(self, tapes):
        """
        Broadcast tapes for batch execution (if necessary)
        """
        if all(tape.batch_size for tape in tapes):
            expanded_tapes, _ = map_batch_transform(broadcast_expand, tapes)
            return expanded_tapes

        return tapes

    def process_kwargs(self, kwargs):
        """
        Override original method from `pennylane_qiskit.qiskit_device.QiskitDevice`
        to avoid accessing backend property, unnecessary init of service
        """
        self.compile_backend = None
        self.set_transpile_args(**kwargs)
        self.run_args = kwargs.copy()

    def map_wires(self, wires):
        """
        Override original method from `pennylane._device.Device`,
        because produces incorrect results.

        # TODO: why?

        Using dummy method for now.
        """
        return wires

    def convert_result(self, qscript):
        """
        wraps native QiskitDevice return value conversion from `self._samples`
        """
        if not pennylane.active_return():
            res = self._statistics_legacy(qscript)
        else:
            res = self.statistics(qscript)

        return res

    def get_execution_metadata(self, result, qscript):
        """
        metadata corresponding to the given result-qscript pair
        """
        return {
            "result_object": result,
            "num_measurements": len(qscript.measurements),
        }

    @abstractmethod
    def post_process(self, qscripts_list, results) -> Tuple[List[Any], List[dict]]:
        """
        Post process a primitive's result object into  the form expected
        from an equivalent QNode.
        """
        raise NotImplementedError()


class _SamplerDevice(_PennylaneQiskitDevice):

    def _samples_from_distribution(self, dist):
        """
        override QiskitDevice.generate_samples to work with primitive
        """

        dist_bin = dist.binary_probabilities()

        bit_strings = list(dist_bin)
        probs = [dist_bin[bs] for bs in bit_strings]

        # generate artificial samples from quasi-distribution probabilities
        bit_samples = np.random.choice(bit_strings, size=self.shots, p=probs)
        return np.vstack([np.array([int(i) for i in s[::-1]]) for s in bit_samples])

    def post_process(self, qscripts_list, results) -> Tuple[List[Any], List[dict]]:
        """
        - when the Qelectron is called with a single input:

        qscripts_list = [qscript]
        results       = [[SamplerResult[dist]]]

        - when the Qelectron is called with a vector input:

        qscripts_list = [qscript]
        results       = [[SamplerResult[dist, ..., dist]]]

        - when the Qelectron is called through `qml.grad`:

        qscripts_list = [qscript, qscript]
        results       = [[SamplerResult[dist]], [SamplerResult[dist]]]
        """
        pp_results = []
        metadatas = []

        for result, qscript in zip(results, qscripts_list):

            spl_result_obj = result.pop()
            qs_conv_results = []
            qs_metadatas = []

            for dist in spl_result_obj.quasi_dists:
                self._samples = self._samples_from_distribution(dist)
                qs_conv_results.extend(self.convert_result(qscript))
                qs_metadatas.append(self.get_execution_metadata(spl_result_obj, qscript))

            metadatas.extend(qs_metadatas)

            if len(qs_conv_results) > 1:
                pp_results.append(qs_conv_results)
            else:
                pp_results.extend(qs_conv_results)

        pp_results = self._asarray(pp_results)
        return pp_results, metadatas


class _LocalQiskitDevice:

    def __init__(self):
        self._circuit = None
        self.transpile_args = {}

    def compile(self):
        """
        Used to override original method from `pennylane_qiskit.qiskit_device.QiskitDevice`
        to always use a `None` compile backend
        """
        return transpile(self._circuit, backend=None, **self.transpile_args)


class _QiskitRuntimeDevice:

    @classmethod
    def request_result(cls, job):
        if not pennylane.active_return():
            job = job.pop()

        return job.result()
