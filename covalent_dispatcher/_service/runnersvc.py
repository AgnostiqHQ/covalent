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


from enum import Enum

from fastapi import APIRouter

from covalent._shared_files import logger
from covalent._shared_files.util_classes import Status

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()


class ResultStatus(str, Enum):
    cancelled = "cancelled"
    completed = "completed"
    failed = "failed"


@router.put("/update/task/{dispatch_id}/{node_id}/{status}")
async def update_task_status(dispatch_id: str, node_id: int, status: ResultStatus):
    # Dummy impl for now

    from .._core import runner_exp

    task_metadata = {
        "dispatch_id": dispatch_id,
        "node_id": node_id,
    }
    detail = {"status": Status(status.value.upper())}
    await runner_exp.mark_task_ready(task_metadata, detail)
    app_log.debug(f"Marked task {dispatch_id}:{node_id} with status {status}")
    return f"Task {task_metadata} marked ready"
