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

"""
Tests for the core functionality of the runner.
"""


from unittest.mock import AsyncMock

import pytest
from sqlalchemy.pool import StaticPool

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent.executor.base import AsyncBaseExecutor
from covalent_dispatcher._core.runner_exp import _submit_abstract_task
from covalent_dispatcher._dal.result import Result as SRVResult
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db import update
from covalent_dispatcher._db.datastore import DataStore

TEST_RESULTS_DIR = "/tmp/results"


class MockExecutor(AsyncBaseExecutor):
    SUPPORTS_MANAGED_EXECUTION = True

    async def run(self, function, args, kwargs, task_metadata):
        pass

    def get_upload_uri(self, task_metadata, object_key):
        return f"file:///tmp/{object_key}"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.lattice(deps_bash=ct.DepsBash(["ls"]))
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(received_workflow, "pipeline_workflow")

    return result_object


def get_mock_srvresult(sdkres, test_db) -> SRVResult:

    sdkres._initialize_nodes()

    update.persist(sdkres)

    return get_result_object(sdkres.dispatch_id)


@pytest.mark.asyncio
async def test_submit_abstract_task(mocker):

    import datetime

    me = MockExecutor()
    me.send = AsyncMock(return_value="42")

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.get_electron_attribute",
        return_value="managed_dask",
    )

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.get_executor",
        return_value=me,
    )

    ts = datetime.datetime.now()

    node_result = {
        "node_id": 0,
        "start_time": ts,
        "status": "RUNNING",
    }

    mocker.patch(
        "covalent_dispatcher._core.runner_exp.datamgr.generate_node_result",
        return_value=node_result,
    )

    mock_upload = mocker.patch(
        "covalent_dispatcher._core.data_modules.asset_manager.upload_asset_for_nodes",
    )

    dispatch_id = "dispatch"
    task_id = 0
    name = "task"
    abstract_inputs = {"args": [1], "kwargs": {"key": 2}}
    task_metadata = {"dispatch_id": dispatch_id, "node_id": task_id}

    mock_function_uri = me.get_upload_uri(task_metadata, "function")
    mock_deps_uri = me.get_upload_uri(task_metadata, "deps")
    mock_cb_uri = me.get_upload_uri(task_metadata, "call_before")
    mock_ca_uri = me.get_upload_uri(task_metadata, "call_after")
    mock_node_upload_uri_1 = me.get_upload_uri(task_metadata, "node_1")
    mock_node_upload_uri_2 = me.get_upload_uri(task_metadata, "node_2")

    await _submit_abstract_task(dispatch_id, task_id, name, abstract_inputs)

    mock_upload.assert_awaited()

    me.send.assert_awaited_with(
        mock_function_uri,
        mock_deps_uri,
        mock_cb_uri,
        mock_ca_uri,
        [mock_node_upload_uri_1],
        {"key": mock_node_upload_uri_2},
        task_metadata,
    )
