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

"""This module contains all the functions required interface with the jobs table"""

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from covalent._shared_files import logger

from .datastore import workflow_db
from .models import Electron, Job, Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class MissingJobRecordError(Exception):
    """
    Exception to be raised when the job record associated with a particular task is not found in the database
    """

    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)


def transaction_get_job_record(session: Session, job_id: int) -> Dict:
    """
    Query the database for the job record associated with the given job id using the passed in session
    Session object is passed to ensure that for all db related calls the same session is used

    Arg(s)
        session: SQLalchemy session object
        job_id: ID of the job to query

    Return(s)
        Dictionary of the job record from the database
    """
    if job_record := session.query(Job).where(Job.id == job_id).first():
        return {
            "job_id": job_record.id,
            "cancel_requested": job_record.cancel_requested,
            "cancel_successful": job_record.cancel_successful,
            "job_handle": job_record.job_handle,
        }
    else:
        raise MissingJobRecordError(message=f"Job {job_id} not found")


def _update_job_record(
    session: Session,
    job_id: int,
    cancel_requested: bool = None,
    cancel_successful: bool = None,
    job_handle: str = None,
):
    """
    Update the job record in the database

    Arg(s)
        session: SQLalchemy session object
        job_id: ID of the job to update
        cancel_requested: Boolean flag indicating whether the job was requested to be cancelled
        cancel_successful: Boolean indicating whether the job was cancelled successfully
        job_handle: Unique job handle returned by the execution backend

    Return(s)
        None
    """
    job_record = session.query(Job).where(Job.id == job_id).first()
    if not job_record:
        raise MissingJobRecordError(message=f"Job {job_id} not found")

    if cancel_requested is not None:
        job_record.cancel_requested = cancel_requested
    if cancel_successful is not None:
        job_record.cancel_successful = cancel_successful
    if job_handle is not None:
        job_record.job_handle = job_handle


def get_job_record(job_id: int) -> Dict:
    """
    Retrive the job record from database

    Arg(s)
        job_id: ID of the job to be returned

    Return(s)
        Job record of the job identified by `job_id`
    """
    return get_job_records([job_id])[0]


def update_job_records(record_kwargs_list: list):
    """
    Update job records in the database

    Arg(s)
        record_kwargs_list: List of keyword arguments of the fields that need to be updated in the job records

    Return(s)
        None
    """
    with workflow_db.session() as session:
        for entry in record_kwargs_list:
            _update_job_record(session, **entry)


def get_job_records(job_ids: List[int]) -> List[Dict]:
    """
    Retrieve the job records of all jobs with `job_ids`

    Arg(s)
        job_ids: List of job ids to query the job records of

    Return(s)
        Job records of all tasks with `job_ids`
    """
    with workflow_db.session() as session:
        records = list(map(lambda x: transaction_get_job_record(session, x), job_ids))
    return records


def to_job_ids(dispatch_id: str, task_ids: List[int]) -> List[int]:
    """
    Map all lattice task ids to their corresponding job ids

    Arg(s)
        dispatch_id: Dispatch ID of the lattice
        task_ids: IDs of tasks in the lattice

    Return(s)
        Corresponding job ids assocated with the provided task ids
    """
    with workflow_db.session() as session:
        stmt = select(Lattice).where(Lattice.dispatch_id == dispatch_id)
        lattice_rec = session.scalars(stmt).first()
        if not lattice_rec:
            raise KeyError(f"Invalid dispatch {dispatch_id}")

        stmt = (
            select(Electron.job_id)
            .where(Electron.parent_lattice_id == lattice_rec.id)
            .where(Electron.transport_graph_node_id.in_(task_ids))
        )

        records = session.scalars(stmt).all()

        return records
