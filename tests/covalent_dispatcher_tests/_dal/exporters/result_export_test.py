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

"""Tests for exporting Result -> ResultSchema"""

import tempfile

import pytest

import covalent as ct
from covalent._results_manager.result import Result as SDKResult
from covalent._serialize.result import serialize_result
from covalent._shared_files.schemas.result import ResultSchema
from covalent_dispatcher._dal.exporters.result import export_result
from covalent_dispatcher._dal.importers.result import import_result
from covalent_dispatcher._dal.result import Result
from covalent_dispatcher._db.datastore import DataStore

TEMP_RESULTS_DIR = "/tmp/covalent_result_import_test"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def get_mock_manifest(dispatch_id, tmpdir) -> ResultSchema:
    """Construct a mock result object corresponding to a lattice."""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def workflow(x):
        res1 = task(x)
        return res1

    workflow.build_graph(x=1)

    sdk_res = SDKResult(workflow, dispatch_id=dispatch_id)

    return serialize_result(sdk_res, tmpdir)


def test_export_result(mocker, test_db):
    dispatch_id = "test_export_result"

    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    with (
        tempfile.TemporaryDirectory(prefix="covalent-") as sdk_dir,
        tempfile.TemporaryDirectory(prefix="covalent-") as srv_dir,
    ):
        manifest = get_mock_manifest(dispatch_id, sdk_dir)
        received_manifest = manifest.copy(deep=True)
        filtered_res = import_result(received_manifest, srv_dir, None)

    srvres = Result.from_dispatch_id(dispatch_id, bare=False)

    exported = export_result(srvres)

    assert exported.metadata == manifest.metadata
    assert exported.lattice.metadata == manifest.lattice.metadata

    tg_export = exported.lattice.transport_graph
    tg = manifest.lattice.transport_graph

    assert len(tg.nodes) == len(tg_export.nodes)
    assert len(tg.links) == len(tg_export.links)

    for i, node in enumerate(tg.nodes):
        assert node.id == tg_export.nodes[i].id
        assert node.metadata == tg_export.nodes[i].metadata

    for i, edge in enumerate(tg.links):
        assert edge == tg.links[i]
