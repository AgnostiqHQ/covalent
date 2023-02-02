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

"""Interface to the Jobs table"""

from typing import List

from ..._db.jobdb import get_job_records, to_job_ids, update_job_records


class JobManager:
    """Interface to the electrons Jobs table in DB"""

    @staticmethod
    def _set_cancel_requested(job_ids: List[int]) -> None:
        records = [{"job_id": job_id, "cancel_requested": True} for job_id in job_ids]
        update_job_records(records)

    @staticmethod
    async def set_cancel_requested(dispatch_id: str, task_ids: List[int]):
        job_ids = to_job_ids(dispatch_id, task_ids)
        JobManager._set_cancel_requested(job_ids)

    @staticmethod
    async def get_jobs_metadata(dispatch_id: str, task_ids: List[int]) -> List:
        job_ids = to_job_ids(dispatch_id, task_ids)
        return get_job_records(job_ids)

    @staticmethod
    async def _set_job_metadata(dispatch_id: str, task_id: int, **kwargs):
        job_id = to_job_ids(dispatch_id, [task_id])[0]
        update_kwargs = kwargs
        update_kwargs["job_id"] = job_id
        update_job_records([update_kwargs])

    @staticmethod
    async def set_job_handle(dispatch_id: str, task_id: int, job_handle: str):
        await JobManager._set_job_metadata(dispatch_id, task_id, job_handle=job_handle)

    @staticmethod
    async def set_cancel_result(dispatch_id: str, task_id: int, cancel_status: bool):
        await JobManager._set_job_metadata(dispatch_id, task_id, cancel_successful=cancel_status)
