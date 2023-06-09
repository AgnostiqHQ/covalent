"""Pennylane-Qiskit devices to Quantum Electrons"""
from typing import Any, List, Tuple, Union

from pennylane import active_return
from qiskit.primitives import Estimator as LocalEstimator
from qiskit.primitives import Sampler as LocalSampler
from qiskit_ibm_runtime import Estimator, Sampler

from .utils import (Measurement, PennylaneQiskitError, convert_qscripts,
                    extract_options)
from .wrappers import (_EstimatorDevice, _LocalQiskitDevice,
                       _PennylaneQiskitDevice, _QiskitRuntimeDevice,
                       _SamplerDevice)


class QiskitLocalSampler(_LocalQiskitDevice, _SamplerDevice):
    """
    Pennylane device that runs circuits using the local `qiskit.primitives.Sampler`
    """

    short_name = "local_sampler"

    supported_measurements = [
        Measurement.EXPVAL,
        Measurement.SAMPLE,
        Measurement.COUNTS,
        Measurement.VAR,
        Measurement.PROBS,
    ]

    def __init__(self, wires: int, shots: int, **_):

        _LocalQiskitDevice.__init__(self)
        _SamplerDevice.__init__(
            self,
            wires=wires,
            shots=shots,
            backend_name="None",
            service_init_kwargs={},
        )

    def batch_execute(self, circuits):
        jobs = []
        sampler = LocalSampler()
        for circuit in circuits:
            tapes = self.broadcast_tapes([circuit])
            compiled_circuits = self.compile_circuits(tapes)  # NOTE: slow step
            job = sampler.run(compiled_circuits)
            jobs.append(job)

        return [[job.result()] for job in jobs]


class QiskitLocalEstimator(_LocalQiskitDevice, _EstimatorDevice):
    """
    Pennylane device that runs circuits using the local `qiskit.primitives.Estimator`
    """

    short_name = "local_estimator"

    supported_measurements = [
        Measurement.EXPVAL,
    ]

    def __init__(self, wires: int, shots: int, **_):

        _LocalQiskitDevice.__init__(self)
        _EstimatorDevice.__init__(
            self,
            wires=wires,
            shots=shots,
            backend_name="None",
            service_init_kwargs={},
        )

    def batch_execute(self, circuits):
        jobs = []
        estimator = LocalEstimator()
        for circuit in circuits:
            tapes = self.broadcast_tapes([circuit])
            compiled_circuits = self.compile_circuits(tapes)  # NOTE: slow step
            compiled_circuits_ops, observables = convert_qscripts(compiled_circuits)

            job = estimator.run(compiled_circuits_ops, observables)
            jobs.append(job)

        return [[job.result()] for job in jobs]


class QiskitRuntimeSampler(_QiskitRuntimeDevice, _SamplerDevice):
    """
    Pennylane device that runs circuits with Qiskit Runtime's `Sampler`
    """

    short_name = "sampler"

    supported_measurements = (
        Measurement.EXPVAL,
        Measurement.SAMPLE,
        Measurement.COUNTS,
        Measurement.VAR,
        Measurement.PROBS,
    )

    def __init__(
        self,
        wires: int,
        shots: int,
        backend_name: str,
        max_time: Union[int, str],
        options: dict,
        service_init_kwargs: dict,
    ):

        _options = extract_options(options)
        _options.execution.shots = shots
        self.options = _options
        self.max_time = max_time

        _SamplerDevice.__init__(
            self,
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            service_init_kwargs=service_init_kwargs,
        )

    def batch_execute(self, circuits):

        with super().session(  # pylint: disable=not-context-manager
            self.service,
            self.backend,
            self.max_time
        ) as session:

            sampler = Sampler(session=session, options=self.options)
            jobs = []
            for circuit in circuits:
                tapes = self.broadcast_tapes([circuit])
                compiled_circuits = self.compile_circuits(tapes)  # NOTE: slow step
                job = sampler.run(compiled_circuits)
                jobs.append(job)

        if not active_return():
            jobs = [[job] for job in jobs]

        return jobs

    def post_process(self, qscripts_list, results) -> Tuple[List[Any], List[dict]]:
        results = [[self.request_result(job)] for job in results]
        return _SamplerDevice.post_process(self, qscripts_list, results)


class QiskitRuntimeEstimator(_QiskitRuntimeDevice, _EstimatorDevice):
    """
    Pennylane device that runs circuits using Qiskit Runtime's `Estimator`
    """

    short_name = "estimator"

    supported_measurements = (
        Measurement.EXPVAL,
    )

    def __init__(
        self,
        wires: int,
        shots: int,
        backend_name: str,
        max_time: Union[int, str],
        options: dict,
        service_init_kwargs: dict,
    ):

        _options = extract_options(options)
        _options.execution.shots = shots
        self.options = _options
        self.max_time = max_time

        _EstimatorDevice.__init__(
            self,
            wires=wires,
            shots=shots,
            backend_name=backend_name,
            service_init_kwargs=service_init_kwargs,
        )

    def batch_execute(self, circuits):

        with super().session(  # pylint: disable=not-context-manager
            self.service,
            self.backend,
            self.max_time
        ) as session:

            estimator = Estimator(session=session, options=self.options)
            jobs = []
            for circuit in circuits:
                tapes = self.broadcast_tapes([circuit])
                compiled_circuits = self.compile_circuits(tapes)  # NOTE: slow step
                compiled_circuits_ops, observables = convert_qscripts(compiled_circuits)
                job = estimator.run(compiled_circuits_ops, observables)
                jobs.append(job)

        if not active_return():
            jobs = [[job] for job in jobs]

        return jobs

    def post_process(self, qscripts_list, results) -> Tuple[List[Any], List[dict]]:
        results = [[self.request_result(job)] for job in results]
        return _EstimatorDevice.post_process(self, qscripts_list, results)


class _pennylane_qiskit_devices:

    """
    singleton that tracks Pennylane-Qiskit device implementations and
    measurement compatibilities
    """

    _instance = None

    def __new__(cls):

        if cls._instance is None:
            # map short names to device classes
            subclasses = cls.get_all_subclasses(_PennylaneQiskitDevice)
            subclass_map = {
                device_cls.short_name: device_cls for device_cls in subclasses
            }

            if len(subclasses) != len(subclass_map):
                raise RuntimeError("duplicate short names in qiskit devices")

            # map supported measurements to device classes
            measurements_map = {}
            for short_name, device_cls in subclass_map.items():
                for meas_type in device_cls.supported_measurements:
                    if meas_type in measurements_map:
                        measurements_map[meas_type].append(short_name)
                    else:
                        measurements_map[meas_type] = [short_name]

            # assign maps to singleton instance
            cls._instance = super(_pennylane_qiskit_devices, cls).__new__(cls)
            cls._instance.device_map = subclass_map
            cls._instance.measurements_map = measurements_map

        return cls._instance

    @classmethod
    def get_all_subclasses(cls, target_cls):
        """
        recursively get all subclasses of target class
        """
        subclasses = []

        for sub_cls in target_cls.__subclasses__():
            subclasses.append(sub_cls)
            subclasses.extend(cls.get_all_subclasses(sub_cls))

        return [sc for sc in subclasses if not sc.__name__.startswith("_")]


def get_device_cls(name):
    """
    Get a Pennylane-Qiskit device class by name
    """
    # pylint: disable=no-member
    dev_cls = _pennylane_qiskit_devices().device_map.get(name)
    if dev_cls is None:
        raise ValueError(f"unknown device name '{name}'.")
    return dev_cls


def create_device(name: str, **kwargs):
    """
    Create a Qiskit device by name
    """
    return get_device_cls(name)(**kwargs)


def validate_device(name: str, meas_type: str):
    """
    Check device support for the given measurement
    """
    dev_cls = get_device_cls(name)

    if meas_type not in dev_cls.supported_measurements:
        # pylint: disable=no-member
        supported_dev_names = _pennylane_qiskit_devices().measurements_map.get(meas_type, [])
        devices_str = ", ".join(["'" + d + "'" for d in supported_dev_names])

        msg = f"qml.{meas_type} measurement is not supported for '{name}' device"
        if len(supported_dev_names) == 0:
            msg += "; no QElectron devices support this measurement."
        else:
            msg += f"; compatible devices are {devices_str}."

        raise PennylaneQiskitError(msg)

    return name
