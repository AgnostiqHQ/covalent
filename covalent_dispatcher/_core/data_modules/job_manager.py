# Copyright 2023 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# """Interface to the Jobs table"""

from typing import Any, List

from ..._db.jobdb import get_job_records, to_job_ids, update_job_records


def _set_cancel_requested(job_ids: List[int]) -> None:
    """
    Update the job record with `cancel_requested`= True (private to module)

    Arg(s)
        job_ids: List of all job ids that have been requested to be cancelled

    Return(s)
        None
    """
    records = [{"job_id": job_id, "cancel_requested": True} for job_id in job_ids]
    update_job_records(records)


async def set_cancel_requested(dispatch_id: str, task_ids: List[int]):
    """
    Set all the task with `task_ids` to be cancelled

    Arg(s)
        dispatch_id: Dispatch ID of the workflow
        task_ids: List of task ids to be cancelled

    Return(s)
        None
    """
    job_ids = to_job_ids(dispatch_id, task_ids)
    _set_cancel_requested(job_ids)


async def get_jobs_metadata(dispatch_id: str, task_ids: List[int]) -> Any:
    """
    Retrive all job records with task_ids for the given dispatch

    Arg(s)
        dispatch_id: Dispatch ID
        task_ids: List of task ids

    Return(s)
        Dictionary of job metdata associated with each task
    """
    job_ids = to_job_ids(dispatch_id, task_ids)
    return get_job_records(job_ids)


async def _set_job_metadata(dispatch_id: str, task_id: int, **kwargs) -> None:
    """
    Store any metadata associated with a job to the database

    Arg(s)
        dispatch_id: Dispatch ID of the the lattice
        task_id: ID of the task in the lattice
        kwargs: Keyword arguments

    Return(s)
        None
    """
    job_id = to_job_ids(dispatch_id, [task_id])[0]
    update_kwargs = kwargs
    update_kwargs["job_id"] = job_id
    update_job_records([update_kwargs])


async def set_job_handle(dispatch_id: str, task_id: int, job_handle: str) -> None:
    """
    Set the job handle of the task to the database

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task in the lattice
        job_handle: Job handle returned by the backend corresponding to the task (JSONable)

    Return(s)
        None
    """
    await _set_job_metadata(dispatch_id, task_id, job_handle=job_handle)


async def set_job_status(dispatch_id: str, task_id: int, status: str) -> None:
    """
    Update the status of the job in the database

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_id: ID of the task in the lattice
        status: status

    Return(s)
        None
    """
    await _set_job_metadata(dispatch_id, task_id, job_status=status)
