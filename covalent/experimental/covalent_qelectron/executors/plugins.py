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

from typing import List, Union

import pennylane as qml

from ..executors.base import (
    BaseProcessPoolQExecutor,
    BaseQExecutor,
    BaseThreadPoolQExecutor,
    QCResult,
    SyncBaseQExecutor,
    get_thread_pool,
)
from .qiskit.qiskit_executor import QiskitExecutor

__all__ = [
    "QiskitExecutor",
    "IBMQExecutor",
    "Simulator",
]


class IBMQExecutor(BaseThreadPoolQExecutor):

    device: str = "qiskit.ibmq"
    backend: str = "ibmq_qasm_simulator"
    ibmqx_token: str = None
    hub: str = "ibm-q"
    group: str = "open"
    project: str = "main"
    max_jobs: int = 20

    def batch_submit(self, qscripts_list: List[qml.tape.qscript.QuantumScript]):

        p = get_thread_pool(self.max_jobs)
        jobs = []
        for qscript in qscripts_list:
            dev = qml.device(
                self.device,
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


class Simulator(BaseQExecutor):

    device: str = "default.qubit"
    parallel: Union[bool, str] = "process"
    workers: int = None

    def batch_submit(self, qscripts_list):

        if self.parallel == "process":
            self.backend = BaseProcessPoolQExecutor(n_jobs=self.workers, device=self.device)
        elif self.parallel == "thread":
            self.backend = BaseThreadPoolQExecutor(max_workers=self.workers, device=self.device)
        else:
            self.backend = SyncBaseQExecutor(device=self.device)

        return self.backend.batch_submit(qscripts_list)

    def batch_get_result_and_time(self, futures_list):
        return self.backend.batch_get_result_and_time(futures_list)
