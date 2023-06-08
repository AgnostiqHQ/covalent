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

import asyncio
import time
from typing import Any, List, Optional, Union

import pennylane as qml

from ..base import AsyncBaseQExecutor, QCResult, get_asyncio_event_loop
from .devices import QiskitLocalSampler, QiskitRuntimeSampler
from .utils import RuntimeOptions

__all__ = [
    "QiskitExecutor",
]

_DEVICE_NAMES_MAP = {
    "local_sampler": QiskitLocalSampler,
    "sampler": QiskitRuntimeSampler,
}


def create_device(device_name: str, **kwargs):
    """
    Allows for the creation of a custom Pennylane-Qiskit device from a string name.
    """
    device_cls = _DEVICE_NAMES_MAP.get(device_name)
    if not device_cls:
        raise ValueError(f"Unsupported Qiskit primitive device '{device_name}'.")
    return device_cls(**kwargs)


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

        # initialize a device: QiskitRuntimeEstimator, QiskitRuntimeSampler, etc.
        dev = create_device(
            self.device,
            wires=qscripts_list[0].wires,
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
