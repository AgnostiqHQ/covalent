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

"""This module contains all the functions required interface with the jobs table"""

from typing import Dict, List

from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .datastore import workflow_db
from .models import Job

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class MissingJobRecordError(Exception):
    pass


def _update_job_record(
    session: Session,
    job_id: int,
    cancel_requested: bool = None,
    cancel_successful: bool = None,
    job_handle: str = None,
):

    job_record = session.query(Job).where(Job.id == job_id).first()

    if not job_record:
        raise MissingJobRecordError

    if cancel_requested is not None:
        job_record.cancel_requested = cancel_requested
    if cancel_successful is not None:
        job_record.cancel_successful = cancel_successful
    if job_handle is not None:
        job_record.job_handle = job_handle


def txn_get_job_record(session: Session, job_id: int) -> Dict:
    job_record = session.query(Job).where(Job.id == job_id).first()

    if not job_record:
        raise MissingJobRecordError

    return {
        "job_id": job_record.id,
        "cancel_requested": job_record.cancel_requested,
        "cancel_successful": job_record.cancel_successful,
        "job_handle": job_record.job_handle,
    }


def get_job_record(job_id: int) -> Dict:
    return get_job_records([job_id])[0]


def update_job_records(record_kwargs_list: list):
    with workflow_db.session() as session:
        for entry in record_kwargs_list:
            _update_job_record(session, **entry)


def get_job_records(job_ids: List[int]) -> Dict:
    with workflow_db.session() as session:
        records = list(map(lambda x: txn_get_job_record(session, x), job_ids))
    return records
