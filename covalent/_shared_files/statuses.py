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


import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from util_classes import SafeVariable

    from .._results_manager.result import Result


@dataclass
class Status:
    executor_name = "_AbstractBaseExecutor"
    category_name = ""
    status_name = ""
    description = "Default status description"

    def get_identifier(self):
        return ":".join((self.executor_name, self.category_name, self.status_name))


# Pending Statuses
class PendingStatus(Status):
    category_name = "Pending"
    description = "Task exists in the dispatch database but has not been invoked by the dispatcher"


# Running Statuses
class RunningStatus(Status):
    category_name = "Running"
    description = "Task is currently executing"


# Completed Statuses
class CompletedStatus(Status):
    category_name = "Completed"
    description = "Task completed successfully"


# Cancelled Statuses
class CancelledStatus(Status):
    category_name = "Cancelled"
    description = "Task was cancelled by the user"


# Failed Statuses
class FailedStatus(Status):
    category_name = "Failed"
    description = "Execution of task has failed"


class ConnectionLostStatus(FailedStatus):
    status_name = "ConnectionLost"
    description = "Connection to remote backend lost"


class TimeoutStatus(FailedStatus):
    status_name = "Timeout"
    description = "Task exceeded the time limit and was terminated"


async def status_listener(
    result_object: "Result", node_id: int, status_store: "SafeVariable"
) -> None:
    while True:
        current_status = status_store.retrieve()
        if isinstance(current_status, (None, PendingStatus, RunningStatus)):
            result_object._update_node(node_id=node_id, status=current_status)
            await asyncio.sleep(0)
        else:
            result_object._update_node(node_id=node_id, status=current_status)
            break
