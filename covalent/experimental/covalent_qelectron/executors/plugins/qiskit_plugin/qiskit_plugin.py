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
from typing import Optional, Union

import pennylane as qml
from pydantic import Field

from covalent._shared_files.config import get_config
from covalent.experimental.covalent_qelectron.executors.base import (
    AsyncBaseQExecutor,
    BaseThreadPoolQExecutor,
    QCResult,
    get_asyncio_event_loop,
    get_thread_pool,
)
from covalent.experimental.covalent_qelectron.executors.plugins.qiskit_plugin.local_sampler import QiskitLocalSampler
from covalent.experimental.covalent_qelectron.executors.plugins.qiskit_plugin.runtime_sampler import QiskitRuntimeSampler
from covalent.experimental.covalent_qelectron.executors.plugins.qiskit_plugin.utils import RuntimeOptions
from covalent.experimental.covalent_qelectron.shared_utils import import_from_path

__all__ = [
    "IBMQExecutor",
    "QiskitExecutor",
]

_QEXECUTOR_PLUGIN_DEFAULTS = {

    "IBMQExecutor": {
        "backend": "ibmq_qasm_simulator",
        "ibmqx_token": "",
        "hub": "ibm-q",
        "group": "open",
        "project": "main",
    },

    "QiskitExecutor": {
        "device": "local_sampler",
        "backend": "ibmq_qasm_simulator",
        "ibmqx_token": "",
        "hub": "ibm-q",
        "group": "open",
        "project": "main",
        "options": {
            "optimization_level": 3,
            "resilience_level": 1,
        }
    },
}


class IBMQExecutor(BaseThreadPoolQExecutor):

    max_jobs: int = 20

    backend: str = Field(
        default_factory=lambda: get_config("qelectron")["IBMQExecutor"]["backend"]
    )
    ibmqx_token: str = Field(
        default_factory=lambda: get_config("qelectron")["IBMQExecutor"]["ibmqx_token"]
    )
    hub: str = Field(
        default_factory=lambda: get_config("qelectron")["IBMQExecutor"]["hub"]
    )
    group: str = Field(
        default_factory=lambda: get_config("qelectron")["IBMQExecutor"]["group"]
    )
    project: str = Field(
        default_factory=lambda: get_config("qelectron")["IBMQExecutor"]["project"]
    )

    def batch_submit(self, qscripts_list):

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "qiskit.ibmq",
                wires=qscript.wires,
                backend=self.backend,
                ibmqx_token=self.ibmqx_token,
                hub=self.hub,
                group=self.group,
                project=self.project,
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            jobs.append(p.submit(self.run_circuit, qscript, dev, result_obj))

        return jobs


class QiskitExecutor(AsyncBaseQExecutor):

    """
    Executor that submits Pennylane Circuits to Qiskit Runtime
    """

    shots: Optional[int] = 1024
    max_time: Union[int, str] = None
    ibmqx_url: str = None
    channel: str = "ibm_quantum"
    instance: str = ""
    cloud_instance: str = ""

    device: str = Field(
        default_factory=lambda: get_config("qelectron")["QiskitExecutor"]["device"]
    )
    backend: str = Field(
        default_factory=lambda: get_config("qelectron")["QiskitExecutor"]["backend"]
    )
    ibmqx_token: str = Field(
        default_factory=lambda: get_config("qelectron")["QiskitExecutor"]["ibmqx_token"]
    )
    hub: str = Field(
        default_factory=lambda: get_config("qelectron")["QiskitExecutor"]["hub"]
    )
    group: str = Field(
        default_factory=lambda: get_config("qelectron")["QiskitExecutor"]["group"]
    )
    project: str = Field(
        default_factory=lambda: get_config("qelectron")["QiskitExecutor"]["project"]
    )
    options: RuntimeOptions = Field(
        # pylint: disable=unnecessary-lambda
        default_factory=lambda: RuntimeOptions(
            **get_config("qelectron")["QiskitExecutor"]["options"]
        )
    )

    def batch_submit(self, qscripts_list):

        qscripts_list = list(qscripts_list)
        self._validate(qscripts_list)

        # keyword argument for compatible custom devices
        device_init_kwargs = {
            "wires": self.qnode_device_wires,
            "shots": self.qnode_device_shots or self.shots,
            "backend_name": self.backend,
            "max_time": self.max_time,
            "options": self.options or {},
            "service_init_kwargs": {
                'ibmqx_token': self.ibmqx_token,
                'ibmqx_url': self.ibmqx_url,
                'channel': self.channel,
                'instance': self.instance,
                'cloud_instance': self.cloud_instance,
                'hub': self.hub,
                'group': self.group,
                'project': self.project
            },
        }

        # initialize a custom Pennylane device
        dev = _execution_device_factory(
            self.device,
            qnode_device_cls=import_from_path(self.qnode_device_import_path),
            **device_init_kwargs,
        )

        # set `pennylane.active_return()` status
        dev.pennylane_active_return = self.pennylane_active_return  # pylint: disable=attribute-defined-outside-init

        # initialize a result object
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

    async def run_circuit(self, tapes, device, result_obj: QCResult):  # pylint: disable=arguments-renamed
        """
        Allows circuits to be submitted asynchronously using `.run_later()`.
        """
        start_time = time.perf_counter()
        results = qml.execute(tapes, device, None)

        await asyncio.sleep(0)

        results, metadatas = device.post_process(tapes, results)
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time
        result_obj.metadata["execution_metadata"].extend(metadatas)

        return result_obj

    def _validate(self, qscripts):
        """
        Perform necessary checks on the qscripts.
        """
        # check that all qscripts have the same number of wires
        if any(qs.wires != qscripts[0].wires for qs in qscripts[1:]):
            raise RuntimeError("All qscripts must use the same wires.")


_DEVICE_MAP = {
    "local_sampler": QiskitLocalSampler,
    "sampler": QiskitRuntimeSampler,
}


def _execution_device_factory(device_name: str, qnode_device_cls, **kwargs):
    """
    Allows for the creation of a custom Pennylane-Qiskit device from a string name.
    """
    custom_device_cls = _DEVICE_MAP.get(device_name)
    if not custom_device_cls:
        raise ValueError(f"Unsupported Qiskit primitive device '{device_name}'.")

    class _QiskitExecutionDevice(custom_device_cls, qnode_device_cls):
        # pylint: disable=too-few-public-methods

        """
        Wrapper that inherits from a Pennylane device class to extend the custom
        Pennylane-Qiskit device with any device-specific overridden methods.
        """

    return _QiskitExecutionDevice(**kwargs)
