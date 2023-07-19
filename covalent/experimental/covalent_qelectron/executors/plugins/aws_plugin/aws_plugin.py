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

from braket.aws import AwsQuantumTask, AwsQuantumTaskBatch

from covalent._shared_files.config import get_config
from covalent.experimental.covalent_qelectron.executors.base import (
    AsyncBaseQExecutor,
    BaseThreadPoolQExecutor,
    BaseQExecutor,
    QCResult,
    get_asyncio_event_loop,
    get_thread_pool
)
from covalent.experimental.covalent_qelectron.shared_utils import import_from_path

__all__ = [
    "BraketQubitExecutor",
    "LocalBraketQubitExecutor"
]

_QEXECUTOR_PLUGIN_DEFAULTS = {

    "BraketQubitExecutor": {
        "device_arn": "",
        "s3_destination_folder": ""
    },

    "LocalBraketQubitExecutor": {
        "backend": "default"
    }
} 

class BraketQubitExecutor(BaseThreadPoolQExecutor):

    max_jobs: int = 20
    device_arn: str = None
    poll_timeout_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_TIMEOUT
    poll_interval_seconds: float = AwsQuantumTask.DEFAULT_RESULTS_POLL_INTERVAL
    aws_session: Optional[str] = None # not actually a str. Fix.
    parallel: bool = False
    max_parallel: Optional[int] = None
    max_connections: int = AwsQuantumTaskBatch.MAX_CONNECTIONS_DEFAULT
    max_retries: int = AwsQuantumTaskBatch.MAX_RETRIES
    run_kwargs: dict = {}
    s3_destination_folder: str = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["s3_destination_folder"]
    )
    def batch_submit(self, qscripts_list):

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.aws.qubit",
                wires=qscript.wires,
                device_arn=self.device_arn,
                s3_destination_folder=self.s3_destination_folder,
                shots=self.shots,
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
    
class LocalBraketQubitExecutor(BaseThreadPoolQExecutor):
    
    max_jobs: int = 20
    shots: int = None
    run_kwargs: dict = {}
    backend: str = Field(
        default_factory=lambda: get_config("qelectron")["LocalBraketQubitExecutor"]["backend"]
    )

    def batch_submit(self, qscripts_list):

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.local.qubit",
                wires=qscript.wires,
                backend=self.backend,
                shots=self.shots,
                **self.run_kwargs
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            jobs.append(p.submit(self.run_circuit, qscript, dev, result_obj))

        return jobs
