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

from typing import Optional

import pennylane as qml
from braket.aws import AwsQuantumTask, AwsQuantumTaskBatch
from pydantic import Field

from covalent._shared_files.config import get_config
from covalent.executor.qbase import BaseThreadPoolQExecutor, QCResult, get_thread_pool

__all__ = ["BraketQubitExecutor", "LocalBraketQubitExecutor"]

_QEXECUTOR_PLUGIN_DEFAULTS = {
    "BraketQubitExecutor": {
        "device_arn": "",
        "poll_timeout_seconds": AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        "poll_interval_seconds": AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        "max_connections": AwsQuantumTaskBatch.MAX_CONNECTIONS_DEFAULT,
        "max_retries": AwsQuantumTaskBatch.MAX_RETRIES,
    },
    "LocalBraketQubitExecutor": {
        "backend": "default",
    },
}


class BraketQubitExecutor(BaseThreadPoolQExecutor):
    """
    The remote Braket executor based on the existing Pennylane Braket
    qubit device. Usage of this device requires valid AWS credentials as
    set up following the instructions at
    https://github.com/aws/amazon-braket-sdk-python#prerequisites.

    Attributes:
        max_jobs:
            maximum number of parallel jobs sent by threads on :code:`batch_submit`.
        shots: number of shots used to estimate quantum observables.
        device_arn:
            an alpha-numeric code (arn=Amazon Resource Name) specifying a quantum device.
        poll_timeout_seconds:
            number of seconds before a poll to remote device is considered timed-out.
        poll_interval_seconds:
            number of seconds between polling of a remote device's status.
        aws_session:
            An :code:`AwsSession` object created to manage interactions with AWS services,
            to be supplied if extra control is desired.
        parallel: turn parallel execution on or off.
        max_parallel: the maximum number of circuits to be executed in parallel.
        max_connections: the maximum number of connections in the :code:`Boto3` connection pool.
        max_retries: the maximum number of time a job will be re-sent if it failed
        s3_destination_folder: Name of the S3 bucket and folder, specified as a tuple.
        run_kwargs: Variable length keyword arguments for :code:`braket.devices.Device.run()`

    """

    device_arn: str = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["device_arn"]
    )
    poll_timeout_seconds: float = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"][
            "poll_timeout_seconds"
        ]
    )
    poll_interval_seconds: float = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"][
            "poll_interval_seconds"
        ]
    )
    max_connections: int = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["max_connections"]
    )
    max_retries: int = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["max_retries"]
    )
    max_jobs: int = 20
    aws_session: Optional[str] = None  # not actually a str. Fix.
    parallel: bool = False
    max_parallel: Optional[int] = None
    s3_destination_folder: tuple = ()
    run_kwargs: dict = {}

    def batch_submit(self, qscripts_list):
        """
        Submit qscripts for execution using :code:`max_jobs`-many threads.

        Args:
            qscripts_list: a list of Pennylane style :code:`QuantumScripts`

        Returns:
            jobs: a :code:`list` of tasks subitted by threads.
        """

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.aws.qubit",
                wires=self.qelectron_info.device_wires,
                device_arn=self.device_arn,
                s3_destination_folder=self.s3_destination_folder,
                shots=self.override_shots,
                poll_timeout_seconds=self.poll_timeout_seconds,
                poll_interval_seconds=self.poll_interval_seconds,
                aws_session=self.aws_session,
                parallel=self.parallel,
                max_parallel=self.max_parallel,
                max_connections=self.max_connections,
                max_retries=self.max_retries,
                **self.run_kwargs,
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            jobs.append(p.submit(self.run_circuit, qscript, dev, result_obj))

        return jobs

    def dict(self, *args, **kwargs):
        dict_ = super().dict(*args, **kwargs)
        # needed to make the dict method hashable and jsonable
        dict_["run_kwargs"] = tuple(dict_["run_kwargs"].items())
        return dict_


class LocalBraketQubitExecutor(BaseThreadPoolQExecutor):
    """
    The local Braket executor based on the existing Pennylane local Braket qubit device.

    Attributes:
        max_jobs: maximum number of parallel jobs sent by processes on :code:`batch_submit`.
        shots: number of shots used to estimate quantum observables.
        backend:
            The name of the simulator backend. Defaults to the :code:`"default"`
            simulator backend name.
        run_kwargs: Variable length keyword arguments for :code:`braket.devices.Device.run()`.
    """

    backend: str = Field(
        default_factory=lambda: get_config("qelectron")["LocalBraketQubitExecutor"]["backend"]
    )
    max_jobs: int = 20
    run_kwargs: dict = {}

    def batch_submit(self, qscripts_list):
        """
        Submit qscripts for execution using :code:`num_threads`-many threads.

        Args:
            qscripts_list: a list of Pennylane style :code:`QuantumScripts`.

        Returns:
            jobs: a :code:`list` of tasks subitted by threads.
        """

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.local.qubit",
                wires=self.qelectron_info.device_wires,
                backend=self.backend,
                shots=self.override_shots,
                **self.run_kwargs,
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            jobs.append(p.submit(self.run_circuit, qscript, dev, result_obj))

        return jobs

    def dict(self, *args, **kwargs):
        dict_ = super().dict(*args, **kwargs)
        # needed to make the dict method hashable and jsonable
        dict_["run_kwargs"] = tuple(dict_["run_kwargs"].items())
        return dict_
