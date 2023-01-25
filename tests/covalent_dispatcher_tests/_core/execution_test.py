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
Integration tests for the dispatcher, runner, and result modules
"""

import asyncio
from typing import Dict, List

import pytest
import pytest_asyncio
from sqlalchemy.pool import StaticPool

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import run_workflow
from covalent_dispatcher._core.execution import _get_task_inputs
from covalent_dispatcher._dal.result import Result as SRVResult
from covalent_dispatcher._dal.result import get_result_object
from covalent_dispatcher._db import models, update
from covalent_dispatcher._db.datastore import DataStore

TEST_RESULTS_DIR = "/tmp/results"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


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

    with test_db.session() as session:
        record = session.query(models.Lattice).where(models.Lattice.id == 1).first()

    update.persist(sdkres)

    return get_result_object(sdkres.dispatch_id)


@pytest.mark.asyncio
async def test_get_task_inputs(mocker, test_db):
    """Test _get_task_inputs for both dicts and list parameter types"""

    @ct.electron
    def list_task(arg: List):
        return len(arg)

    @ct.electron
    def dict_task(arg: Dict):
        return len(arg)

    @ct.electron
    def multivariable_task(x, y):
        return x, y

    @ct.lattice
    def list_workflow(arg):
        return list_task(arg)

    @ct.lattice
    def dict_workflow(arg):
        return dict_task(arg)

    #    1   2
    #     \   \
    #      0   3
    #     / /\/
    #     4   5

    @ct.electron
    def identity(x):
        return x

    @ct.lattice
    def multivar_workflow(x, y):
        electron_x = identity(x)
        electron_y = identity(y)
        res1 = multivariable_task(electron_x, electron_y)
        res2 = multivariable_task(electron_y, electron_x)
        res3 = multivariable_task(electron_y, electron_x)
        res4 = multivariable_task(electron_x, electron_y)
        return 1

    # list-type inputs

    list_workflow.build_graph([1, 2, 3])
    serialized_args = [ct.TransportableObject(i) for i in [1, 2, 3]]

    # Nodes 0=task, 1=:electron_list:, 2=1, 3=2, 4=3
    sdkres = Result(lattice=list_workflow, dispatch_id="asdf")
    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    result_object = get_mock_srvresult(sdkres, test_db)
    tg = result_object.lattice.transport_graph
    tg.set_node_value(2, "output", ct.TransportableObject(1))
    tg.set_node_value(3, "output", ct.TransportableObject(2))
    tg.set_node_value(4, "output", ct.TransportableObject(3))

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )
    task_inputs = await _get_task_inputs(1, tg.get_node_value(1, "name"), result_object)

    expected_inputs = {"args": serialized_args, "kwargs": {}}

    assert task_inputs == expected_inputs

    # dict-type inputs

    dict_workflow.build_graph({"a": 1, "b": 2})
    serialized_args = {"a": ct.TransportableObject(1), "b": ct.TransportableObject(2)}

    # Nodes 0=task, 1=:electron_dict:, 2=1, 3=2
    sdkres = Result(lattice=dict_workflow, dispatch_id="asdf_dict_workflow")
    result_object = get_mock_srvresult(sdkres, test_db)
    tg = result_object.lattice.transport_graph
    tg.set_node_value(2, "output", ct.TransportableObject(1))
    tg.set_node_value(3, "output", ct.TransportableObject(2))

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )
    task_inputs = await _get_task_inputs(1, tg.get_node_value(1, "name"), result_object)
    expected_inputs = {"args": [], "kwargs": serialized_args}

    assert task_inputs == expected_inputs

    # Check arg order
    multivar_workflow.build_graph(1, 2)
    received_lattice = Lattice.deserialize_from_json(multivar_workflow.serialize_to_json())
    sdkres = Result(lattice=received_lattice, dispatch_id="asdf_multivar_workflow")
    result_object = get_mock_srvresult(sdkres, test_db)
    tg = result_object.lattice.transport_graph

    # Account for injected postprocess electron
    assert list(tg._graph.nodes) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    tg.set_node_value(0, "output", ct.TransportableObject(1))
    tg.set_node_value(2, "output", ct.TransportableObject(2))

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    task_inputs = await _get_task_inputs(4, tg.get_node_value(4, "name"), result_object)

    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [1, 2]

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    task_inputs = await _get_task_inputs(5, tg.get_node_value(5, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [2, 1]

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    task_inputs = await _get_task_inputs(6, tg.get_node_value(6, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [2, 1]

    mock_get_result = mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    task_inputs = await _get_task_inputs(7, tg.get_node_value(7, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [1, 2]


@pytest.mark.asyncio
async def test_run_workflow_with_failing_nonleaf(mocker, test_db):
    """Test running workflow with a failing intermediate node"""

    @ct.electron
    def failing_task(x):
        assert False

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        res2 = failing_task(res1)
        return res2

    from covalent._workflow.lattice import Lattice

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    sdkres = Result(lattice)
    sdkres._dispatch_id = dispatch_id
    sdkres._root_dispatch_id = dispatch_id
    sdkres._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    result_object = get_mock_srvresult(sdkres, test_db)

    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )

    msg_queue = asyncio.Queue()
    mock_status_queues = {result_object.dispatch_id: msg_queue}
    mocker.patch("covalent_dispatcher._core.dispatcher._status_queues", mock_status_queues)
    mock_get_incomplete_nodes = mocker.patch(
        "covalent_dispatcher._core.data_manager.get_incomplete_tasks",
        return_value={"failed": [(0, "failing_task")], "cancelled": []},
    )

    status = await run_workflow(result_object.dispatch_id)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert status == Result.FAILED
    mock_get_incomplete_nodes.assert_awaited()
    assert result_object.error == "The following tasks failed:\n0: failing_task"


@pytest.mark.asyncio
async def test_run_workflow_with_failing_leaf(mocker, test_db):
    """Test running workflow with a failing leaf node"""

    @ct.electron
    def failing_task(x):
        assert False
        return x

    @ct.lattice
    def workflow(x):
        res1 = failing_task(x)
        return res1

    from covalent._workflow.lattice import Lattice

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf_failing_leaf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    sdkres = Result(lattice)
    sdkres._dispatch_id = dispatch_id
    sdkres._root_dispatch_id = dispatch_id
    sdkres._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    result_object = get_mock_srvresult(sdkres, test_db)

    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )

    msg_queue = asyncio.Queue()
    mock_status_queues = {result_object.dispatch_id: msg_queue}
    mocker.patch("covalent_dispatcher._core.dispatcher._status_queues", mock_status_queues)
    mock_get_failed_nodes = mocker.patch(
        "covalent._results_manager.result.Result._get_failed_nodes",
        return_value=[(0, "failing_task")],
    )

    status = await run_workflow(result_object.dispatch_id)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert status == Result.FAILED
    assert result_object.error == "The following tasks failed:\n0: failing_task"


@pytest.mark.asyncio
async def test_run_workflow_normal(mocker, test_db):
    """Test running workflow with a failing leaf node"""

    @ct.electron
    def square(x):
        return x**2

    @ct.lattice
    def workflow(x):
        return square(x)

    from covalent._workflow.lattice import Lattice

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf_normal"
    lattice = Lattice.deserialize_from_json(json_lattice)
    sdkres = Result(lattice)
    sdkres._dispatch_id = dispatch_id
    sdkres._root_dispatch_id = dispatch_id
    sdkres._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.utils.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.tg.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.base.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._dal.result.workflow_db", test_db)

    result_object = get_mock_srvresult(sdkres, test_db)

    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )

    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_result_object", return_value=result_object
    )

    msg_queue = asyncio.Queue()
    mock_status_queues = {result_object.dispatch_id: msg_queue}
    mocker.patch("covalent_dispatcher._core.dispatcher._status_queues", mock_status_queues)

    status = await run_workflow(result_object.dispatch_id)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert status == Result.COMPLETED


async def test_run_workflow_does_not_deserialize(mocker):
    """Check that dispatcher does not deserialize user data when using
    out-of-process `workflow_executor`"""

    from dask.distributed import LocalCluster

    from covalent._workflow.lattice import Lattice
    from covalent.executor import DaskExecutor

    lc = LocalCluster()
    dask_exec = DaskExecutor(lc.scheduler_address)

    @ct.electron(executor=dask_exec)
    def task(x):
        return x

    @ct.lattice(executor=dask_exec, workflow_executor=dask_exec)
    def workflow(x):
        # Exercise both sublatticing and postprocessing
        sublattice_task = ct.lattice(task, workflow_executor=dask_exec)
        res1 = ct.electron(sublattice_task(x), executor=dask_exec)
        return res1

    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    dispatch_id = "asdf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, lattice.metadata["results_dir"])
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.datastore.DataStore.factory", return_value=test_db)
    mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )
    update.persist(result_object)

    mock_to_deserialize = mocker.patch("covalent.TransportableObject.get_deserialized")

    status = await run_workflow(result_object.dispatch_id)

    mock_to_deserialize.assert_not_called()
    assert status == Result.COMPLETED
