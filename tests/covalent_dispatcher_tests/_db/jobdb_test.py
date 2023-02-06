from datetime import datetime as dt
from datetime import timezone

import pytest

from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._db.jobdb import (
    MissingJobRecordError,
    get_job_record,
    to_job_ids,
    update_job_records,
)
from covalent_dispatcher._db.models import Job, Lattice
from covalent_dispatcher._db.write_result_to_db import insert_electrons_data, insert_lattices_data

from .write_result_to_db_test import get_electron_kwargs, get_lattice_kwargs


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database"""
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

    with pytest.raises(MissingJobRecordError):
        get_job_record(42)


def test_update_job_records(test_db, mocker):
    mocker.patch("covalent_dispatcher._db.jobdb.workflow_db", test_db)
    with test_db.session() as session:
        job = Job(cancel_requested=False, job_handle="aws_job_id_1")
        session.add(job)

        job = Job(cancel_requested=False, job_handle="aws_job_id_2")
        session.add(job)

    job_1_kwargs = {"job_id": 1, "cancel_requested": True, "cancel_successful": True}
    job_2_kwargs = {"job_id": 2, "cancel_requested": True, "job_handle": "42"}

    update_job_records([job_1_kwargs, job_2_kwargs])

    record_1 = get_job_record(1)
    record_2 = get_job_record(2)
    assert record_1["cancel_requested"] is True
    assert record_1["cancel_successful"] is True
    assert record_2["cancel_requested"] is True
    assert record_2["cancel_successful"] is False

    with pytest.raises(MissingJobRecordError):
        update_job_records([{"job_id": 5, "cancel_requested": True}])


def test_to_job_ids(test_db, mocker):

    mocker.patch("covalent_dispatcher._db.jobdb.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    cur_time = dt.now(timezone.utc)
    lattice_kwargs = get_lattice_kwargs(
        dispatch_id="test_dispatch", created_at=cur_time, updated_at=cur_time, started_at=cur_time
    )
    insert_lattices_data(**lattice_kwargs)

    with test_db.session() as session:
        rows = session.query(Lattice).all()
        assert len(rows) == 1

    electron_kwargs = {
        **get_electron_kwargs(
            parent_dispatch_id="test_dispatch",
            transport_graph_node_id=0,
            cancel_requested=False,
            created_at=cur_time,
            updated_at=cur_time,
        )
    }

    insert_electrons_data(**electron_kwargs)

    electron_kwargs = {
        **get_electron_kwargs(
            parent_dispatch_id="test_dispatch",
            transport_graph_node_id=1,
            cancel_requested=False,
            created_at=cur_time,
            updated_at=cur_time,
        )
    }

    insert_electrons_data(**electron_kwargs)

    job_ids = to_job_ids("test_dispatch", [0])
    assert job_ids == [1]

    job_ids = to_job_ids("test_dispatch", [0, 1])
    assert job_ids == [1, 2]
