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

"""Tests for DB-backed Result"""


import os
import tempfile

import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._core.data_modules import asset_manager as am
from covalent_dispatcher._dal.result import Result, get_result_object
from covalent_dispatcher._db import update
from covalent_dispatcher._db.datastore import DataStore

TEMP_RESULTS_DIR = os.environ.get("COVALENT_DATA_DIR") or ct.get_config("dispatcher.results_dir")


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
        res2 = task(res1)
        return res2

    workflow.build_graph(x=1)
    received_workflow = SDKLattice.deserialize_from_json(workflow.serialize_to_json())
    result_object = SDKResult(received_workflow, "mock_dispatch")

    return result_object


def get_mock_srvresult(sdkres, test_db) -> Result:

    sdkres._initialize_nodes()

    update.persist(sdkres)

    return get_result_object(sdkres.dispatch_id)


@pytest.mark.asyncio
async def test_upload_asset_for_nodes(test_db, mocker):
    sdkres = get_mock_result()
    sdkres._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    srvres = get_mock_srvresult(sdkres, test_db)

    srvres.lattice.transport_graph.set_node_value(0, "stdout", "Hello!\n")
    srvres.lattice.transport_graph.set_node_value(2, "stdout", "Bye!\n")

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path_0 = temp.name

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        dest_path_2 = temp.name

    dest_uri_0 = os.path.join("file://", dest_path_0)
    dest_uri_2 = os.path.join("file://", dest_path_2)

    await am.upload_asset_for_nodes(srvres.dispatch_id, "stdout", {0: dest_uri_0, 2: dest_uri_2})

    with open(dest_path_0, "r") as f:
        assert f.read() == "Hello!\n"

    with open(dest_path_2, "r") as f:
        assert f.read() == "Bye!\n"

    os.unlink(dest_path_0)
    os.unlink(dest_path_2)


@pytest.mark.asyncio
async def test_download_assets_for_node(test_db, mocker):
    sdkres = get_mock_result()
    sdkres._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    srvres = get_mock_srvresult(sdkres, test_db)

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        stdout_path = temp.name

    with tempfile.NamedTemporaryFile("w", delete=True, suffix=".txt") as temp:
        stderr_path = temp.name

    with open(stdout_path, "w") as f:
        assert f.write("Hello\n")

    with open(stderr_path, "w") as f:
        assert f.write("Bye\n")

    stdout_uri = os.path.join("file://", stdout_path)
    stderr_uri = os.path.join("file://", stderr_path)

    await am.download_assets_for_node(
        srvres.dispatch_id, 0, {"stdout": stdout_uri, "stderr": stderr_uri}
    )

    assert srvres.lattice.transport_graph.get_node_value(0, "stdout") == "Hello\n"
    assert srvres.lattice.transport_graph.get_node_value(0, "stderr") == "Bye\n"

    os.unlink(stdout_path)
    os.unlink(stderr_path)
