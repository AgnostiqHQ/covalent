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

from covalent._shared_files.config import get_config
from covalent.experimental.covalent_qelectron.executors.base import (
    BaseProcessPoolQExecutor,
    BaseQExecutor,
    BaseThreadPoolQExecutor,
    SyncBaseQExecutor,
)


class Simulator(BaseQExecutor):

    """
    Local executor that uses process or thread-based parallelism to execute circuits.
    """

    device: str = get_config("qelectron")["device"]

    parallel: Union[bool, str] = "thread"
    workers: int = 10
    backend: BaseQExecutor = None

    def batch_submit(self, qscripts_list):

        if self.parallel == "process":
            self.backend = BaseProcessPoolQExecutor(num_processes=self.workers, device=self.device)
        elif self.parallel == "thread":
            self.backend = BaseThreadPoolQExecutor(num_threads=self.workers, device=self.device)
        else:
            self.backend = SyncBaseQExecutor(device=self.device)

        return self.backend.batch_submit(qscripts_list)

    def batch_get_results(self, futures_list):
        return self.backend.batch_get_results(futures_list)
