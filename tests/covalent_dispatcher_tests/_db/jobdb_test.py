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

"""Unit tests for the module used to interface with the jobs table"""

import pytest

from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.jobdb import get_job_record, update_job_records
from covalent_dispatcher._db.models import Job


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def test_get_job_record(test_db, mocker):
    mocker.patch("covalent_dispatcher._db.jobdb.workflow_db", test_db)
    with test_db.session() as session:
        job = Job(cancel_requested=True, job_handle="aws_job_id")
        session.add(job)

    record = get_job_record(1)
    assert record["job_handle"] == "aws_job_id"


def test_update_job_records(test_db, mocker):
    mocker.patch("covalent_dispatcher._db.jobdb.workflow_db", test_db)
    with test_db.session() as session:
        job = Job(cancel_requested=False, job_handle="aws_job_id_1")
        session.add(job)

        job = Job(cancel_requested=False, job_handle="aws_job_id_2")
        session.add(job)

    job_1_kwargs = {"job_id": 1, "cancel_requested": True, "cancel_successful": True}
    job_2_kwargs = {"job_id": 2, "cancel_requested": True}

    update_job_records([job_1_kwargs, job_2_kwargs])

    record_1 = get_job_record(1)
    record_2 = get_job_record(2)
    assert record_1["cancel_requested"] is True
    assert record_1["cancel_successful"] is True
    assert record_2["cancel_requested"] is True
    assert record_2["cancel_successful"] is False
