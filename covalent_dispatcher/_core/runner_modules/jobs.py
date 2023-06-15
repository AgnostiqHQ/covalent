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

""" Handlers for the executor proxy """


from covalent._shared_files import logger
from covalent._shared_files.util_classes import Status
from covalent_dispatcher._core import data_manager as datamgr

from .. import data_manager as datasvc
from ..data_modules import job_manager
from .utils import get_executor

app_log = logger.app_log
log_stack_info = logger.log_stack_info


async def get_cancel_requested(dispatch_id: str, task_id: int):
    """
    Query the database for the task's cancellation status

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice

    Return(s)
        Canellation status of the task
    """

    app_log.debug(f"Get _handle_requested for task {dispatch_id}:{task_id}")
    job_records = await job_manager.get_jobs_metadata(dispatch_id, [task_id])
    app_log.debug(f"Job record: {job_records[0]}")
    return job_records[0]["cancel_requested"]


async def get_version_info(dispatch_id: str, task_id: int):
    """
    Query the database for the dispatch version information

    Arg:
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice

    Returns:
        {"python": python_version, "covalent": covalent_version}
    """

    data = await datamgr.lattice.get(dispatch_id, ["python_version", "covalent_version"])

    return {
        "python": data["python_version"],
        "covalent": data["covalent_version"],
    }


async def get_job_status(dispatch_id: str, task_id: int) -> Status:
    """
    Queries the job state for (dispatch_id, task_id)

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice

    Return(s)
        Status
    """
    app_log.debug(f"Get for task {dispatch_id}:{task_id}")
    job_records = await job_manager.get_jobs_metadata(dispatch_id, [task_id])
    app_log.debug(f"Job record: {job_records[0]}")
    return Status(job_records[0]["status"])


async def put_job_handle(dispatch_id: str, task_id: int, job_handle: str) -> bool:
    """
    Store the job handle of the task returned by the backend in the database

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice
        job_handle: Unique identifier of the task returned by the execution backend

    Return(s)
        True
    """
    app_log.debug(f"Put job_handle for executor {dispatch_id}:{task_id}")
    await job_manager.set_job_handle(dispatch_id, task_id, job_handle)
    return True


async def put_job_status(dispatch_id: str, task_id: int, status: Status) -> bool:
    """
    Mark the job for (dispatch_id, task_id) as cancelled

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task within the lattice
        job_status: A `Status` type representing the job status

    Return(s)
        True
    """
    app_log.debug(f"Put cancel result for task {dispatch_id}:{task_id}")
    executor_attrs = await datasvc.electron.get(
        dispatch_id, task_id, ["executor", "executor_data"]
    )
    selected_executor = [executor_attrs["executor"], executor_attrs["executor_data"]]
    executor = get_executor(task_id, selected_executor, None, None)
    if executor.validate_status(status):
        await job_manager.set_job_status(dispatch_id, task_id, str(status))
        return True
    else:
        return False
