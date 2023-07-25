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

from typing import Optional

import pennylane as qml
from pydantic import Field

from braket.aws import AwsQuantumTask, AwsQuantumTaskBatch

from covalent._shared_files.config import get_config
from covalent.experimental.covalent_qelectron.executors.base import (
    BaseProcessPoolQExecutor,
    BaseThreadPoolQExecutor,
    QCResult,
    get_thread_pool,
    get_process_pool
)


__all__ = [
    "BraketQubitExecutor",
    "LocalBraketQubitExecutor"
]

_QEXECUTOR_PLUGIN_DEFAULTS = {

    "BraketQubitExecutor": {
        "device_arn": "",
        "s3_destination_folder": "",
        "poll_timeout_seconds": AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT,
        "poll_interval_seconds": AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL,
        "aws_session": "",
        "parallel": False,
        "max_parallel": None,
        "max_connections": AwsQuantumTaskBatch.MAX_CONNECTIONS_DEFAULT,
        "max_retries": AwsQuantumTaskBatch.MAX_RETRIES,
        "run_kwargs": {},
        "max_jobs": 20
    },

    "LocalBraketQubitExecutor": {
        "backend": "default",
        "shots": None,
        "run_kwargs": {},
        "max_jobs": 20
    }
}


class BraketQubitExecutor(BaseThreadPoolQExecutor):
    """
    The remote Braket executor based on the existing Pennylane Braket
    qubit device. Usage of this device requires valid AWS credentials as
    set up following the instructions at
    https://github.com/aws/amazon-braket-sdk-python#prerequisites.

    Attributes:
        max_jobs:
            maximum number of parallel jobs sent by threads on batch_submit
        shots: number of shots used to estimate quantum observables
        device_arn:
            an alpha-numeric code (arn=Amazon Resource Name) specifying a quantum device
        poll_timeout_seconds:
            number of seconds before a poll to remote device is considered timed-out
        poll_interval_seconds:
            number of seconds between polling of a remote device's status
        aws_session:
            an An AwsSession object created to manage interactions with AWS services,
            to be supplied if extra control is desired.
        parallel: turn parallel execution on or off
        max_parallel: the maximum number of circuits to be executed in parallel
        max_connections: the maximum number of connections in the Boto3 connection pool.
        max_retries: the maximum number of time a job will be re-sent if it failed
        s3_destination_folder: Name of the S3 bucket and folder, specified as a tuple.
        run_kwargs: Variable length keyword arguments for ``braket.devices.Device.run()``

    """

    max_jobs: int = 20
    shots: int = None,
    device_arn: str = None
    poll_timeout_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT
    poll_interval_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL
    aws_session: Optional[str] = None # not actually a str. Fix.
    parallel: bool = False
    max_parallel: Optional[int] = None
    max_connections: int = AwsQuantumTaskBatch.MAX_CONNECTIONS_DEFAULT
    max_retries: int = AwsQuantumTaskBatch.MAX_RETRIES
    s3_destination_folder: tuple = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["s3_destination_folder"]
    )
    run_kwargs: dict = {}

    def batch_submit(self, qscripts_list):
        """
        Submit qscripts for execution using max_jobs-many threads.

        Args:
            qscripts_list: a list of Pennylane style QuantumScripts

        Returns:
            jobs: a list of tasks subitted by threads.
        """

        # Check `self.shots` against 0 to allow override with `None`.
        device_shots = self.shots if self.shots != 0 else self.qnode_device_shots

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.aws.qubit",
                wires=qscript.wires,
                device_arn=self.device_arn,
                s3_destination_folder=self.s3_destination_folder,
                shots=device_shots,
                poll_timeout_seconds=self.poll_timeout_seconds,
                poll_interval_seconds=self.poll_interval_seconds,
                aws_session=self.aws_session,
                parallel=self.parallel,
                max_parallel=self.max_parallel,
                max_connections=self.max_connections,
                max_retries=self.max_retries,
                **self.run_kwargs
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            jobs.append(p.submit(self.run_circuit, qscript, dev, result_obj))

        return jobs
    
    def dict(self, *args, **kwargs):
        dict_ = vars(self)
        dict_["run_kwargs"] = tuple(dict_["run_kwargs"].items())
        return dict_



class LocalBraketQubitExecutor(BaseProcessPoolQExecutor):
    """
    The local Braket executor based on the existing Pennylane local Braket qubit device.

    Attributes:
        max_jobs: maximum number of parallel jobs sent by proccesses on batch_submit
        shots: number of shots used to estimate quantum observables
        backend:
            The name of the simulator backend. Defaults to the ``default``
            simulator backend name.
        run_kwargs: Variable length keyword arguments for ``braket.devices.Device.run()``
    """

    max_jobs: int = 20
    shots: int = None
    backend: str = Field(
        default_factory=lambda: get_config("qelectron")["LocalBraketQubitExecutor"]["backend"]
    )
    run_kwargs: dict = {}

    def batch_submit(self, qscripts_list):
        """
        Submit qscripts for execution using num_processes-many processes.

        Args:
            qscripts_list: a list of Pennylane style QuantumScripts

        Returns:
            jobs: a list of futures subitted by processes
        """

        # Check `self.shots` against 0 to allow override with `None`.
        device_shots = self.shots if self.shots != 0 else self.qnode_device_shots

        pool = get_process_pool(self.num_processes)
        futures = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.local.qubit",
                wires=qscript.wires,
                backend=self.backend,
                shots=device_shots,
                **self.run_kwargs
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            fut = pool.apply_async(self.run_circuit, args=(qscript, dev, result_obj))
            futures.append(fut)

        return futures
    
    def dict(self, *args, **kwargs):
        dict_ = vars(self)
        dict_["run_kwargs"] = tuple(dict_["run_kwargs"].items())
        return dict_
