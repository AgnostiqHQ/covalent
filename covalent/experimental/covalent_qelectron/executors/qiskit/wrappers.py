"""Wrappers for the existing Pennylane-Qiskit interface"""
from abc import abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Callable, Dict, List, Tuple, Union

import numpy as np
import pennylane
from pennylane.transforms import broadcast_expand, map_batch_transform
from pennylane_qiskit.qiskit_device import QiskitDevice
from qiskit.compiler import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Session

from .utils import Measurement


@lru_cache
def _init_runtime_service(
    *,
    ibmqx_token: str = None,
    ibmqx_url: str = None,
    channel: str = "",
    instance: str = "",
    cloud_instance: str = "",
    hub: str = "",
    group: str = "",
    project: str = "",
) -> QiskitRuntimeService:
    """
    Start `QiskitRuntimeService` with specified settings
    """

    if channel == "ibm_quantum":
        if hub and group and project:
            instance = "/".join([hub, group, project])
        elif not instance:
            instance = "ibm-q/open/main"
    elif channel == "ibm_cloud":
        instance = cloud_instance
    else:
        raise ValueError(
            "Invalid `channel` argument, must be either 'ibm_quantum' or 'ibm_cloud'."
        )

    if not instance:
        arg_name = "instance" if channel == "ibm_quantum" else "cloud_instance"
        raise ValueError(
            f"Missing required `{arg_name}` argument for channel type '{channel}'."
        )

    return QiskitRuntimeService(
        channel=channel,
        token=ibmqx_token,
        url=ibmqx_url,
        instance=instance
    )


@dataclass(frozen=True)
class SessionIdentifier:
    """
    Proxy for defining a unique `Session` instance.
    """
    service_channel: str
    service_instance: str
    service_url: str
    backend_name: str
    max_time: Union[int, None]


class _PennylaneQiskitDevice(QiskitDevice):
    """
    A replacement for Pennylane's `QiskitDevice` that uses `QiskitRuntimeService`
    instead of the older `qiskit.providers.provider.ProviderV1`
    """
    _sessions: Dict[SessionIdentifier, Session] = {}

    _type_converters: Dict[Measurement, Callable] = {
        Measurement.EXPVAL: pennylane.numpy.tensor,
        Measurement.SAMPLE: np.asarray,
        Measurement.PROBS: np.asarray,
    }

    name = "Custom Plugin for Pennylane Circuits on Qiskit IBM Runtime"

    @property
    @abstractmethod
    def supported_measurements(self) -> Tuple[Measurement, ...]:
        """
        List of supported Pennylane measurement types
        """

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

    @staticmethod
    def session(service, backend, max_time) -> Session:
        """
        Global Qiskit IBM Runtime sessions, unique up to fields in `SessionIdentifier`
        """
        session_id = _PennylaneQiskitDevice.session_id(service, backend, max_time)
        if session_id not in _PennylaneQiskitDevice._sessions:
            _PennylaneQiskitDevice._sessions[session_id] = Session(
                service=service,
                backend=backend,
                max_time=max_time,
            )

        return _PennylaneQiskitDevice._sessions[session_id]

    @staticmethod
    def session_id(service, backend, max_time) -> SessionIdentifier:
        """
        Create session identifier from `Session` initialization arguments
        """
        return SessionIdentifier(
            service_channel=service._account.channel,  # pylint: disable=protected-access
            service_instance=service._account.instance,  # pylint: disable=protected-access
            service_url=service._account.url,  # pylint: disable=protected-access
            backend_name=backend.name,
            max_time=max_time
        )

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
            self._service = _init_runtime_service(**self.service_init_kwargs)
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
            res = np.asarray(res)
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

    @classmethod
    def get_type_converter(cls, qscript) -> Callable:
        """
        type conversion for the final result, ex. tensor, array, or dict
        """
        meas_types = [repr(m.return_type) for m in qscript.measurements]
        return cls._type_converters.get(meas_types.pop(), lambda x: x)

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
                typ = self.get_type_converter(qscript)
                res = typ([float(r) for r in qs_conv_results])
                pp_results.append(res)
            else:
                typ = self.get_type_converter(qscript)
                res = typ(qs_conv_results)
                pp_results.extend(res)

        return pp_results, metadatas


class _EstimatorDevice(_PennylaneQiskitDevice):

    def post_process(self, qscripts_list, results):
        """
        - when the Qelectron is called with a single input:

        qscripts_list = [qscript]
        results       = [[EstimatorResult[values=[float]]]]

        - when the Qelectron is called with a vector input:

        qscripts_list = [qscript]
        results       = [[EstimatorResult[values=[float, ..., float]]]]

        - when the Qelectron is called through `qml.grad`:

        qscripts_list = [qscript, qscript]
        results       = [[EstimatorResult[values=[float]]]]]
        """
        pp_results = []
        metadatas = []

        for result in results:
            est_result_obj = result.pop()
            if len(est_result_obj.values) > 1:
                typ = self.get_type_converter(qscripts_list.pop())
                res = typ([float(r) for r in est_result_obj.values])
                pp_results.append(res)
            else:
                typ = self.get_type_converter(qscripts_list.pop())
                res = typ(est_result_obj.values)
                pp_results.extend(res)

            metadatas.extend(est_result_obj.metadata)

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
