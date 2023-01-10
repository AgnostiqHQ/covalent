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

"""Interface to the Jobs table"""

from typing import List

from ..._db.jobdb import get_job_records, to_job_ids, update_job_records


def _set_cancel_requested(job_ids: List[int]) -> bool:
    records = map(lambda x: {"job_id": x, "cancel_requested": True}, job_ids)
    update_job_records(list(records))


async def set_cancel_requested(dispatch_id: str, task_ids: List[int]):
    job_ids = to_job_ids(dispatch_id, task_ids)
    _set_cancel_requested(job_ids)


async def get_job_metadata(dispatch_id: str, task_id: int):
    record = await get_jobs_metadata(dispatch_id, [task_id])
    return record[0]


async def get_jobs_metadata(dispatch_id: str, task_ids: List[int]):
    job_ids = to_job_ids(dispatch_id, task_ids)
    return get_job_records(job_ids)


async def set_job_metadata(dispatch_id: str, task_id: int, **kwargs):
    job_id = to_job_ids(dispatch_id, [task_id])[0]
    update_kwargs = kwargs
    update_kwargs["job_id"] = job_id
    update_job_records([update_kwargs])


async def set_job_handle(dispatch_id: str, task_id: int, job_handle: str):
    await set_job_metadata(dispatch_id, task_id, job_handle=job_handle)


async def set_cancel_result(dispatch_id: str, task_id: int, cancel_status: bool):
    await set_job_metadata(dispatch_id, task_id, cancel_successful=cancel_status)
