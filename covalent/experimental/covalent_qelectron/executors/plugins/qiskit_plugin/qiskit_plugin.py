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
from pennylane.tape.qscript import QuantumScript
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

_DEVICE_MAP = {
    "local_sampler": QiskitLocalSampler,
    "sampler": QiskitRuntimeSampler,
}


class IBMQExecutor(BaseThreadPoolQExecutor):
    """
    A quantum executor that uses the Pennylane native "qiskit.ibmq" device to run
    circuits on IBM Quantum backends. The attributes `backend`, `ibmqx_token`,
    `hub`, `group`, and `project` are taken from the Covalent configuration file
    by default, if available.

    Keyword Args:
        max_jobs: The maximum number of jobs that can be submitted to the backend
            concurrently. This number corresponds to the number of threads utilized
            by this executor. Defaults to 20.
       shots: The number of shots to use for the execution device. Overrides the
            :code:`shots` value from the original device if set to :code:`None` or
            a positive :code:`int`. The shots setting from the original device is
            is used by default, when this argument is 0.
        backend: The name of the IBM Quantum backend device. Defaults to
            "ibmq_qasm_simulator".
        ibmqx_token: The IBM Quantum API token.
        hub: An IBM Quantum hub name. Defaults to "ibm-q".
        group: An IBM Quantum group name. Defaults to "open".
        project: An IBM Quantum project name. Defaults to "main".

    """

    max_jobs: int = 20
    shots: int = 0

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

        # Check `self.shots` against 0 to allows override with `None`.
        device_shots = self.shots if self.shots != 0 else self.qnode_device_shots

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "qiskit.ibmq",
                wires=self.qnode_device_wires,
                shots=device_shots,
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
    A quantum executor that lets the user run circuits on IBM Quantum backends,
    using runtime sessions and Qiskit primitives. The attributes `device`, `backend`,
    `ibmqx_token`, `hub`, `group`, and `project` are taken from the Covalent
    configuration file by default, if available.

    Keyword Args:
        device: The Qiskit primitive used to execute circuits. Valid values are
            "sampler" and "local_sampler". The value "sampler" corresponds to the
            Qiskit Runtime `Sampler` primitive. The value "local_sampler"
            corresponds to the Qiskit `Sampler` primitive, which is entirely local.
        backend: The name of the IBM Quantum backend device. Defaults to
            "ibmq_qasm_simulator".
        ibmqx_token: The IBM Quantum API token.
        hub: An IBM Quantum hub name. Defaults to "ibm-q".
        group: An IBM Quantum group name. Defaults to "open".
        project: An IBM Quantum project name. Defaults to "main".
        shots: The number of shots to run per circuit. Defaults to 1024.
        single_job: Indicates whether or not all circuits are submitted
            to a single job or as separate jobs. Defaults to True.
        max_time: An optional time limit for circuit execution on the IBM Quantum
            backend. Defaults to `None`, i.e. no time limit.
        local_transpile: Indicates whether or not to transpile circuits before
            submitting to IBM Quantum. Defaults to False.
        ibmqx_url: An optional URL for the Qiskit Runtime API.
        channel: An optional channel for the Qiskit Runtime API. Defaults to
            "ibm_quantum".
        instance: An alternate means to specify `hub`, `group`, and `project`,
            formatted as "{hub}/{group}/{project}".
        cloud_instance: Same as `instance` but for the case `channel="ibm_cloud"`.
        options: A dictionary of options to pass to Qiskit Runtime. See:
            https://qiskit.org/ecosystem/ibm-runtime/stubs/qiskit_ibm_runtime.options.Options.html
            for valid fields.
    """

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

    shots: Optional[int] = 1024
    single_job: bool = False
    local_transpile: bool = False

    max_time: Union[int, str] = None

    ibmqx_url: str = None
    channel: str = "ibm_quantum"
    instance: str = ""
    cloud_instance: str = ""

    options: RuntimeOptions = Field(
        # pylint: disable=unnecessary-lambda
        default_factory=lambda: RuntimeOptions(
            **get_config("qelectron")["QiskitExecutor"]["options"]
        )
    )

    @property
    def device_init_kwargs(self):
        """
        Keyword arguments to pass to the device constructor.
        """
        return {
            "wires": self.qnode_device_wires,
            "shots": self.qnode_device_shots or self.shots,
            "backend_name": self.backend,
            "local_transpile": self.local_transpile,
            "max_time": self.max_time,
            "single_job": self.single_job,
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

    def execution_device(self) -> qml.QubitDevice:
        """
        Create a subclasses execution device that ensure correct output typing.
        """

        # Initialize a custom Pennylane device
        dev = _execution_device_factory(
            self.device,
            qnode_device_cls=import_from_path(self.qnode_device_import_path),
            **self.device_init_kwargs,
        )

        # Set `pennylane.active_return()` status
        dev.pennylane_active_return = self.pennylane_active_return
        return dev

    def batch_submit(self, qscripts_list):

        qscripts_list = list(qscripts_list)

        loop = get_asyncio_event_loop()
        tasks = []

        if self.single_job:
            # All QScripts are submitted as a single job

            # initialize a custom Pennylane device
            dev = self.execution_device()

            # initialize a result object
            result_obj = QCResult.with_metadata(device_name=dev.short_name, executor=self)

            # run qscripts asynchronously
            task = loop.create_task(self.run_all_circuits(qscripts_list, dev, result_obj))
            tasks.append(task)
        else:
            # Each QScript is submitted as a separate job
            for qscript in qscripts_list:
                # initialize a custom Pennylane device
                dev = self.execution_device()

                # initialize a result object
                result_obj = QCResult.with_metadata(device_name=dev.short_name, executor=self)

                # run qscripts asynchronously
                task = loop.create_task(self.run_circuit(qscript, dev, result_obj))
                tasks.append(task)

        return tasks

    async def run_circuit(self, tape, device, result_obj: QCResult):  # pylint: disable=arguments-renamed
        """
        Allows a circuit to be submitted asynchronously.
        """

        start_time = time.perf_counter()
        results = qml.execute([tape], device, None)

        await asyncio.sleep(0)

        results, metadatas = device.post_process(tape, results)
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time
        result_obj.metadata["execution_metadata"].extend(metadatas)

        return result_obj

    async def run_all_circuits(self, tapes, device, result_obj: QCResult):  # pylint: disable=arguments-renamed
        """
        Allows multiple circuits to be submitted asynchronously into a single
        IBM Qiskit Runtime Job.
        """

        start_time = time.perf_counter()
        results = qml.execute(tapes, device, None)

        await asyncio.sleep(0)

        results, metadatas = device.post_process_all(tapes, results)
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time
        result_obj.metadata["execution_metadata"].extend(metadatas)

        return result_obj


def _execution_device_factory(device_name: str, qnode_device_cls, **kwargs):
    """
    Creates a subclassed Pennylane device to ensure correct output typing.
    """
    custom_device_cls = _DEVICE_MAP.get(device_name)
    if not custom_device_cls:
        raise ValueError(f"Unsupported Qiskit primitive device '{device_name}'.")

    class _QiskitExecutionDevice(custom_device_cls, qnode_device_cls):
        # pylint: disable=too-few-public-methods

        pennylane_active_return: bool = True

        """
        Wrapper that inherits from a Pennylane device class to extend the custom
        Pennylane-Qiskit device with any device-specific overridden methods.
        """
        @property
        def stopping_condition(self):
            """
            Needed to target `support_operation` method of `custom_device_cls`.

            NOTE: is identical to `pennylane._device.Device.stopping_condition`.
            """
            return qml.BooleanFn(
                lambda obj: not isinstance(obj, QuantumScript) and self.supports_operation(obj.name)
            )

    return _QiskitExecutionDevice(**kwargs)
