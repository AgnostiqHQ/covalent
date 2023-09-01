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

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent_dispatcher._core.dispatcher import run_workflow
from covalent_dispatcher._core.execution import _get_task_inputs
from covalent_dispatcher._db import update
from covalent_dispatcher._db.datastore import DataStore

TEST_RESULTS_DIR = "/tmp/results"


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
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


def test_get_task_inputs():
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
    tg = list_workflow.transport_graph
    # Nodes 0=task, 1=:electron_list:, 2=1, 3=2, 4=3
    tg.set_node_value(2, "output", ct.TransportableObject(1))
    tg.set_node_value(3, "output", ct.TransportableObject(2))
    tg.set_node_value(4, "output", ct.TransportableObject(3))

    result_object = Result(lattice=list_workflow, dispatch_id="asdf")
    task_inputs = _get_task_inputs(1, tg.get_node_value(1, "name"), result_object)

    expected_inputs = {"args": serialized_args, "kwargs": {}}

    assert task_inputs == expected_inputs

    # dict-type inputs

    dict_workflow.build_graph({"a": 1, "b": 2})
    serialized_args = {"a": ct.TransportableObject(1), "b": ct.TransportableObject(2)}
    tg = dict_workflow.transport_graph
    # Nodes 0=task, 1=:electron_dict:, 2=1, 3=2
    tg.set_node_value(2, "output", ct.TransportableObject(1))
    tg.set_node_value(3, "output", ct.TransportableObject(2))

    result_object = Result(lattice=dict_workflow, dispatch_id="asdf")
    task_inputs = _get_task_inputs(1, tg.get_node_value(1, "name"), result_object)
    expected_inputs = {"args": [], "kwargs": serialized_args}

    assert task_inputs == expected_inputs

    # Check arg order
    multivar_workflow.build_graph(1, 2)
    received_lattice = Lattice.deserialize_from_json(multivar_workflow.serialize_to_json())
    result_object = Result(lattice=received_lattice, dispatch_id="asdf")
    tg = received_lattice.transport_graph

    assert list(tg._graph.nodes) == list(range(9))
    tg.set_node_value(0, "output", ct.TransportableObject(1))
    tg.set_node_value(2, "output", ct.TransportableObject(2))

    task_inputs = _get_task_inputs(4, tg.get_node_value(4, "name"), result_object)

    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [1, 2]

    task_inputs = _get_task_inputs(5, tg.get_node_value(5, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [2, 1]

    task_inputs = _get_task_inputs(6, tg.get_node_value(6, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [2, 1]

    task_inputs = _get_task_inputs(7, tg.get_node_value(7, "name"), result_object)
    input_args = [arg.get_deserialized() for arg in task_inputs["args"]]
    assert input_args == [1, 2]


@pytest.mark.skip(reason="Temp skip")
@pytest.mark.asyncio
async def test_run_workflow_with_failing_nonleaf(mocker):
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
    result_object = Result(lattice)
    result_object._dispatch_id = dispatch_id
    result_object._root_dispatch_id = dispatch_id
    result_object._initialize_nodes()

    # patch all methods that reference a DB
    mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mocker.patch("covalent_dispatcher._db.upsert._electron_data")
    mocker.patch("covalent_dispatcher._db.update.persist")
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_name", return_value="failing_task"
    )
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_error", return_value="AssertionError"
    )
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )
    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )
    mock_get_failed_nodes = mocker.patch(
        "covalent._results_manager.result.Result._get_failed_nodes",
        return_value=[(0, "failing_task")],
    )

    update.persist(result_object)
    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert result_object.status == Result.FAILED

    mock_get_failed_nodes.assert_called()
    assert result_object._error == "The following tasks failed:\n0: failing_task"


@pytest.mark.skip(reason="Temp skip")
@pytest.mark.asyncio
async def test_run_workflow_with_failing_leaf(mocker):
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
    dispatch_id = "asdf"
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice)
    result_object._dispatch_id = dispatch_id
    result_object._root_dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mocker.patch("covalent_dispatcher._db.upsert._electron_data")
    mocker.patch("covalent_dispatcher._db.update.persist")
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_name", return_value="failing_task"
    )
    mocker.patch(
        "covalent._results_manager.result.Result._get_node_error", return_value="AssertionError"
    )
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )
    mock_get_failed_nodes = mocker.patch(
        "covalent._results_manager.result.Result._get_failed_nodes",
        return_value=[(0, "failing_task")],
    )

    update.persist(result_object)

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert result_object.status == Result.FAILED
    assert result_object._error == "The following tasks failed:\n0: failing_task"


@pytest.mark.asyncio
async def test_run_workflow_does_not_deserialize(mocker):
    """Check that dispatcher does not deserialize user data when using
    out-of-process `workflow_executor`"""

    @ct.electron(executor="local")
    def task(x):
        return x

    @ct.lattice(executor="local", workflow_executor="local")
    def workflow(x):
        # Exercise both sublatticing and postprocessing
        sublattice_task = ct.lattice(task, workflow_executor="local")
        res1 = ct.electron(sublattice_task(x), executor="local")
        return res1

    dispatch_id = "asdf"
    workflow.build_graph(5)

    json_lattice = workflow.serialize_to_json()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, dispatch_id=dispatch_id)
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.upsert._lattice_data")
    mocker.patch("covalent_dispatcher._db.upsert._electron_data")
    mocker.patch("covalent_dispatcher._db.update.persist")
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mock_run_abstract_task = mocker.patch("covalent_dispatcher._core.runner._run_abstract_task")
    mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )

    update.persist(result_object)

    mock_to_deserialize = mocker.patch("covalent.TransportableObject.get_deserialized")

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)

    mock_to_deserialize.assert_not_called()
    assert result_object.status == Result.RUNNING
    assert mock_run_abstract_task.call_count == 1


@pytest.mark.asyncio
async def test_run_workflow_with_client_side_postprocess(test_db, mocker):
    """Check that run_workflow handles "client" workflow_executor for
    postprocessing"""

    dispatch_id = "asdf"
    result_object = get_mock_result()
    result_object.lattice.set_metadata("workflow_executor", "client")
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )
    mocker.patch("covalent_dispatcher._core.runner._gather_deps")
    mocker.patch("covalent_dispatcher._core.dispatcher.datasvc.upsert_lattice_data")
    mock_run_abstract_task = mocker.patch("covalent_dispatcher._core.runner._run_abstract_task")

    update.persist(result_object)

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)
    assert result_object.status == Result.RUNNING
    assert mock_run_abstract_task.call_count == 1


@pytest.mark.asyncio
async def test_run_workflow_with_failed_postprocess(test_db, mocker):
    """Check that run_workflow handles postprocessing failures"""

    dispatch_id = "asdf"
    result_object = get_mock_result()
    result_object._dispatch_id = dispatch_id
    result_object._initialize_nodes()

    mocker.patch("covalent_dispatcher._db.write_result_to_db.workflow_db", test_db)
    mocker.patch("covalent_dispatcher._db.upsert.workflow_db", test_db)
    mock_unregister = mocker.patch(
        "covalent_dispatcher._core.dispatcher.datasvc.finalize_dispatch"
    )
    mocker.patch(
        "covalent_dispatcher._core.runner.datasvc.get_result_object", return_value=result_object
    )
    mocker.patch("covalent_dispatcher._core.runner._run_abstract_task")

    update.persist(result_object)

    status_queue = asyncio.Queue()
    mocker.patch(
        "covalent_dispatcher._core.data_manager.get_status_queue", return_value=status_queue
    )
    mock_run_abstract_task = mocker.patch("covalent_dispatcher._core.runner._run_abstract_task")

    def failing_workflow(x):
        assert False

    result_object.lattice.set_metadata("workflow_executor", "bogus")
    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)

    assert result_object.status == Result.RUNNING

    result_object.lattice.workflow_function = ct.TransportableObject(failing_workflow)
    result_object.lattice.set_metadata("workflow_executor", "local")

    result_object = await run_workflow(result_object)
    mock_unregister.assert_called_with(result_object.dispatch_id)

    assert result_object.status == Result.RUNNING
    assert mock_run_abstract_task.call_count == 2
