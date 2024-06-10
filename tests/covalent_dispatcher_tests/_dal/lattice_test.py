# Copyright 2021 Agnostiq Inc.
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

"""Tests for DB-backed electron"""


import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._dal.lattice import ASSET_KEYS, METADATA_KEYS, Lattice
from covalent_dispatcher._dal.result import ASSET_KEYS as DISPATCH_ASSET_KEYS
from covalent_dispatcher._db import models, update
from covalent_dispatcher._db.datastore import DataStore


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_result() -> SDKResult:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x):
        res1 = task(x)
        return res1

    workflow.build_graph(x=1)
    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = SDKResult(received_workflow, "mock_dispatch")

    return result_object


def test_lattice_attributes(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        lat = Lattice(session, record)
        asset_ids = lat.get_asset_ids(session, [])

    assert METADATA_KEYS.issubset(lat.metadata_keys)
    assert asset_ids.keys() == ASSET_KEYS.union(DISPATCH_ASSET_KEYS)

    workflow_function = lat.get_value("workflow_function").get_deserialized()
    assert workflow_function(42) == 42


def test_lattice_restricted_attributes(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        lat = Lattice(session, record, keys=["id"])

    meta = lat.metadata.attrs.keys()
    assert Lattice.meta_record_map("id") in meta
    assert Lattice.meta_record_map("storage_path") not in meta


def test_lattice_get_set_value(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        lat = Lattice(session, record)

    assert lat.get_value("name") == "workflow"
    lat.set_value("executor", "awsbatch")
    lat.set_value("executor_data", {"attributes": {"time_limit": 60}})
    assert lat.get_value("executor") == "awsbatch"
    assert lat.get_value("executor_data") == {"attributes": {"time_limit": 60}}


def test_lattice_get_metadata(test_db, mocker):
    res = get_mock_result()
    res.lattice.metadata["executor"] = "awsbatch"
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Lattice)
            .where(models.Lattice.dispatch_id == "mock_dispatch")
            .first()
        )

        lat = Lattice(session, record)

    assert lat.get_value("executor") == "awsbatch"
