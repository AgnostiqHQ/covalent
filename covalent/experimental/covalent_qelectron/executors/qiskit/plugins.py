import asyncio
import time
from typing import Any, List, Optional, Union

import pennylane as qml

from ..base import AsyncBaseQExecutor, QCResult, get_asyncio_event_loop
from .devices import create_device, validate_device
from .utils import RuntimeOptions

__all__ = [
    "QiskitExecutor",
]


class QiskitExecutor(AsyncBaseQExecutor):

    """
    Executor that submits Pennylane Circuits to Qiskit Runtime
    """

    device: Optional[str] = None
    shots: Union[int, None] = 1024
    service: Any = None
    backend_name: str = "ibmq_qasm_simulator"
    max_time: Union[int, str] = None
    ibmqx_token: str = None
    ibmqx_url: str = None
    channel: str = "ibm_quantum"
    instance: str = ""
    cloud_instance: str = ""
    hub: str = "ibm-q"
    group: str = "open"
    project: str = "main"
    job_retries: int = 5
    max_jobs: int = 20

    # optimization_level, resilience_level, max_execution_time, transpilation_opts
    # resilience_opts, execution_opts, environment_opts, simulator_opts
    options: RuntimeOptions = None

    def batch_submit(self, qscripts_list: List[qml.tape.qscript.QuantumScript]):

        qscripts_list = list(qscripts_list)

        # validate device against measurement type
        wires, device_name = self._validate_qscripts(qscripts_list)

        # initialize a device: QiskitRuntimeEstimator, QiskitRuntimeSampler, etc.
        dev = create_device(
            device_name,
            wires=wires,
            shots=self.shots,
            backend_name=self.backend_name,
            max_time=self.max_time,
            options=self.options or {},
            service_init_kwargs={
                "ibmqx_token": self.ibmqx_token,
                "ibmqx_url": self.ibmqx_url,
                "channel": self.channel,
                "instance": self.instance,
                "cloud_instance": self.cloud_instance,
                "hub": self.hub,
                "group": self.group,
                "project": self.project
            },
        )

        result_obj = QCResult.with_metadata(
            device_name=dev.short_name,
            executor=self,
        )

        # run qscripts asynchronously
        loop = get_asyncio_event_loop()
        task = loop.create_task(
            self.run_circuit(qscripts_list, dev, result_obj)
        )

        return [task]

    async def run_circuit(self, qscripts, device, result_obj: QCResult):  # pylint: disable=arguments-renamed
        """
        Allows circuits to be submitted asynchronously using `.run_later()`.
        Quantum scripts are executed
        """
        start_time = time.perf_counter()
        results = qml.execute(qscripts, device, None)
        await asyncio.sleep(0)
        results, metadatas = device.post_process(qscripts, results)
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time
        result_obj.metadata["execution_metadata"].extend(metadatas)

        return result_obj

    def _validate_qscripts(self, qscripts_list):
        """
        run several checks on quantum scripts to enforce necessary assumptions
        """

        # these must be unique
        device_names = set()
        circuits_wires = set()

        for qscript in qscripts_list:
            for measurement in qscript.measurements:
                meas_type = repr(measurement.return_type)
                device_name = validate_device(self.device, meas_type)

                circuits_wires.add(tuple(qscript.wires))
                device_names.add(device_name)

        # check uniqueness
        if len(device_names) != 1:
            raise RuntimeError("batch of circuits requires multiple device types")
        if len(circuits_wires) != 1:
            raise RuntimeError("wires differ in batch of circuits")

        wires = circuits_wires.pop()
        device_name = device_names.pop()

        return wires, device_name
