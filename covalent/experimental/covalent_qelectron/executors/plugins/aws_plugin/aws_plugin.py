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
from covalent.experimental.covalent_qelectron.shared_utils import import_from_path

__all__ = [
    "BraketQubitExecutor",
]

_QEXECUTOR_PLUGIN_DEFAULTS = {

    "BraketQubitExecutor": {
        "device_arn": "",
        "s3_destination_folder": "",
        # Need AWS session for region etc.
    },
}

class BraketQubitExecutor(BaseThreadPoolQExecutor):

    device_arn: str = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["device_arn"]
    )
    s3_destination_folder: str = Field(
        default_factory=lambda: get_config("qelectron")["BraketQubitExecutor"]["s3_destination_folder"]
    )
     # Need AWS session for region etc.
    def batch_submit(self, qscripts_list):

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                "braket.aws.qubit",
                wires=qscript.wires,
                device_arn=self.device_arn,
                s3_destination_folder=self.s3_destination_folder
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )

            jobs.append(p.submit(self.run_circuit, qscript, dev, result_obj))

        return jobs
