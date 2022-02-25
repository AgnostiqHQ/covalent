# Copyright 2021 Agnostiq Inc.
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

from multiprocessing import Manager

from .base_runner import BaseRunner


class MultiProcRunner(BaseRunner):
    def __init__(self, address):
        self.manager = Manager(
            address=address,
        )

    def run_new_task(self, node_id, task_func, task_args, task_kwargs):
        pass

    def cancel_task(self, node_id):
        pass

    def query_task_status(self, node_id):
        pass
