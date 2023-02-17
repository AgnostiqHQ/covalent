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

"""Tests for DB-backed electron"""


import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._dal.electron import ASSET_KEYS, METADATA_KEYS, Electron
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


def test_electron_attributes(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Electron)
            .where(models.Electron.transport_graph_node_id == 0)
            .first()
        )
        e = Electron(session, record)

    meta = e.pure_metadata.keys()
    assets = e.assets.keys()
    assert meta == METADATA_KEYS
    assert assets == ASSET_KEYS

    assert e.is_asset("output") is True
    assert e.is_asset("status") is False

    assert e.get_value("task_group_id") == e.node_id


def test_electron_get_set_value(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    with test_db.session() as session:
        record = (
            session.query(models.Electron)
            .where(models.Electron.transport_graph_node_id == 0)
            .first()
        )
        e = Electron(session, record)

    assert e.get_value("name") == res.lattice.transport_graph.get_node_value(0, "name")
    assert e.get_value("status") == SDKResult.NEW_OBJ
    assert e.get_value("type") == "function"

    assert e.get_values(["status", "type"]) == {"status": SDKResult.NEW_OBJ, "type": "function"}

    with test_db.session() as session:
        e.set_value("status", SDKResult.RUNNING, session)
        assert e.get_value("status", session) == SDKResult.RUNNING

    e.set_values([("output", 5), ("status", SDKResult.COMPLETED)])
    assert e.get_value("output") == 5
    assert e.get_value("status") == SDKResult.COMPLETED


def test_electron_get_no_refresh(test_db, mocker):
    res = get_mock_result()
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    update.persist(res)

    mock_refresh = mocker.patch("covalent_dispatcher._dal.electron.Electron._refresh_metadata")

    with test_db.session() as session:
        record = (
            session.query(models.Electron)
            .where(models.Electron.transport_graph_node_id == 0)
            .first()
        )
        e = Electron(session, record)

    assert e.get_value("name", refresh=False) == res.lattice.transport_graph.get_node_value(
        0, "name"
    )
    assert e.get_value("status", refresh=False) == SDKResult.NEW_OBJ
    assert e.get_value("type", refresh=False) == "function"

    mock_refresh.assert_not_called()


def test_electron_sub_dispatch_id(test_db, mocker):
    res = get_mock_result()
    res._dispatch_id = "parent_dispatch"
    res._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    update.persist(res, 1)

    with test_db.session() as session:
        record = (
            session.query(models.Electron)
            .where(models.Electron.transport_graph_node_id == 0)
            .first()
        )
        e = Electron(session, record)

    assert e.get_value("sub_dispatch_id") == "parent_dispatch"
