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

from typing import Union

from covalent.experimental.covalent_qelectron.executors.base import (
    BaseProcessPoolQExecutor,
    BaseQExecutor,
    BaseThreadPoolQExecutor,
    SyncBaseQExecutor,
)


class Simulator(BaseQExecutor):
    """
    A quantum executor that uses the specified Pennylane device to execute circuits.
    Parallelizes circuit execution on the specified `device` using either threads
    or processes.

    Keyword Args:
        device: A valid string corresponding to a Pennylane device. Simulation-based 
            devices (e.g. "default.qubit" and "lightning.qubit") are recommended.
            Defaults to "default.qubit".
        parallel: The type of parallelism to use. Valid values are "thread" and
            "process". Passing any other value will result in synchronous execution.
            Defaults to "thread".
        workers: The number of threads or processes to use. Defaults to 10.
        shots: The number of shots to use for the execution device. Overrides the
            :code:`shots` value from the original device if set to :code:`None` or
            a positive :code:`int`. The shots setting from the original device is
            is used by default, when this argument is 0.
    """

    device: str = "default.qubit"
    parallel: Union[bool, str] = "thread"
    workers: int = 10
    shots: int = 0

    _backend: BaseQExecutor = None

    def batch_submit(self, qscripts_list):

        if self.parallel == "process":
            self._backend = BaseProcessPoolQExecutor(num_processes=self.workers, device=self.device)
        elif self.parallel == "thread":
            self._backend = BaseThreadPoolQExecutor(num_threads=self.workers, device=self.device)
        else:
            self._backend = SyncBaseQExecutor(device=self.device)

        # Check `self.shots` against 0 to allow override with `None`.
        device_shots = self.shots if self.shots != 0 else self.qnode_device_shots

        # Pass on server-set settings from original device.
        self._backend.qnode_device_import_path = self.qnode_device_import_path
        self._backend.qnode_device_shots = device_shots
        self._backend.qnode_device_wires = self.qnode_device_wires
        self._backend.pennylane_active_return = self.pennylane_active_return

        return self._backend.batch_submit(qscripts_list)

    def batch_get_results(self, futures_list):
        return self._backend.batch_get_results(futures_list)
