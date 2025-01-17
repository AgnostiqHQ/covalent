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

"""Combined import-export tests"""


import pytest

import covalent as ct
from covalent._results_manager import Result as SDKResult
from covalent._serialize.result import serialize_result
from covalent._workflow.lattice import Lattice as SDKLattice
from covalent_dispatcher._dal.exporters.result import export_result_manifest
from covalent_dispatcher._dal.importers.result import import_result
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


def test_import_export_manifest(test_db, mocker):
    """Check that Export(Import) == identity modulo asset uris"""

    import tempfile

    res = get_mock_result()
    dispatch_id = "test_import_export_manifest"
    res._dispatch_id = dispatch_id
    res._root_dispatch_id = dispatch_id
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)

    with (
        tempfile.TemporaryDirectory() as sdk_tmp_dir,
        tempfile.TemporaryDirectory() as srv_tmp_dir,
    ):
        manifest = serialize_result(res, sdk_tmp_dir)
        received_manifest = manifest.copy(deep=True)

        import_result(received_manifest, srv_tmp_dir, None)

        export_manifest = export_result_manifest(dispatch_id)

        submitted = manifest.dict()
        exported = export_manifest.dict()

        # Check that workflow metadata are preserved
        for key in submitted["metadata"]:
            assert submitted["metadata"][key] == exported["metadata"][key]

        sub_lattice = submitted["lattice"]
        exp_lattice = exported["lattice"]
        for key in sub_lattice["metadata"]:
            assert sub_lattice["metadata"][key] == exp_lattice["metadata"][key]

        # Check workflow assets; uris are filtered by the server
        for key in submitted["assets"]:
            submitted["assets"][key].pop("uri")
            submitted["assets"][key].pop("remote_uri")
            exported["assets"][key].pop("uri")
            exported["assets"][key].pop("remote_uri")
            assert submitted["assets"][key] == exported["assets"][key]

        for key in sub_lattice["assets"]:
            sub_lattice["assets"][key].pop("uri")
            sub_lattice["assets"][key].pop("remote_uri")
            exp_lattice["assets"][key].pop("uri")
            exp_lattice["assets"][key].pop("remote_uri")
            assert sub_lattice["assets"][key] == exp_lattice["assets"][key]

        sub_tg = sub_lattice["transport_graph"]
        exp_tg = exp_lattice["transport_graph"]
        sorted(sub_tg["nodes"], key=lambda x: x["id"])
        sorted(exp_tg["nodes"], key=lambda x: x["id"])

        # Check transport graphs
        for i, sub_node in enumerate(sub_tg["nodes"]):
            exp_node = exp_tg["nodes"][i]
            for key in sub_node["assets"]:
                sub_node["assets"][key].pop("uri")
                sub_node["assets"][key].pop("remote_uri")
                exp_node["assets"][key].pop("uri")
                exp_node["assets"][key].pop("remote_uri")

                assert sub_node["assets"][key] == exp_node["assets"][key]

        assert sub_tg["links"] == exp_tg["links"]
