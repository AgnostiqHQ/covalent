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

from . import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info

if TYPE_CHECKING:
    from util_classes import SafeVariable

    from .._results_manager.result import Result


@dataclass
class Status:
    executor_name = "_AbstractBaseExecutor"
    category_name = "Default"
    status_name = "DefaultStatus"
    description = "Default status description"

    def __str__(self):
        # return self.get_identifier()
        return self.status_name

    def get_identifier(self):
        return ":".join((self.executor_name, self.category_name, self.status_name))


# Pending Statuses
class PendingCategory(Status):
    category_name = "PendingCategory"
    status_name = "PENDING"
    description = "Task exists in the dispatch database but is waiting to be executed"


class PendingPostprocessingStatus(PendingCategory):
    status_name = "PENDING_POSTPROCESSING"
    description = "Task is waiting to be post-processed"


# Running Statuses
class RunningCategory(Status):
    category_name = "RunningCategory"
    status_name = "RUNNING"
    description = "Task is currently executing"


class PostprocessingStatus(RunningCategory):
    status_name = "POSTPROCESSING"
    description = "Task is currently postprocessing"


# Completed Statuses
class CompletedCategory(Status):
    category_name = "CompletedCategory"
    status_name = "COMPLETED"
    description = "Task completed successfully"


# Failed Statuses
class FailedCategory(Status):
    category_name = "FailedCategory"
    status_name = "FAILED"
    description = "Execution of task has failed"


class ConnectionLostStatus(FailedCategory):
    status_name = "ConnectionLost"
    description = "Connection to remote backend lost"


class TimeoutStatus(FailedCategory):
    status_name = "Timeout"
    description = "Task exceeded the time limit and was terminated"


class PostprocessingFailedStatus(FailedCategory):
    status_name = "POSTPROCESSING_FAILED"
    description = "Failed to post-process the task"


# Cancelled Statuses
class CancelledCategory(Status):
    category_name = "CancelledCategory"
    status_name = "CANCELLED"
    description = "Task was cancelled by the user"


async def status_listener(
    result_object: "Result", node_id: int, status_store: "SafeVariable"
) -> None:
    while True:
        try:
            current_status = status_store.retrieve()
            if isinstance(current_status, (type(None), PendingCategory, RunningCategory)):
                node_status = result_object._get_node_status(node_id)
                if node_status != str(current_status):
                    result_object._update_node(node_id=node_id, status=str(current_status))
            else:
                result_object._update_node(node_id=node_id, status=str(current_status))
                break
        except asyncio.CancelledError:
            del status_store
            break


class RESULT_STATUS:
    NEW_OBJECT = str(PendingCategory())
    RUNNING = str(RunningCategory())
    PENDING_POSTPROCESSING = str(PendingPostprocessingStatus())
    POSTPROCESSING = str(PostprocessingStatus())
    COMPLETED = str(CompletedCategory())
    POSTPROCESSING_FAILED = str(PostprocessingFailedStatus())
    FAILED = str(FailedCategory())
    CANCELLED = str(CancelledCategory())
