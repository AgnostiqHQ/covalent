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

"""Unit tests for electron"""

import json
import tempfile
from unittest.mock import ANY, MagicMock

import flake8
import isort
import pytest

import covalent as ct
from covalent._shared_files.context_managers import active_lattice_manager
from covalent._shared_files.defaults import WAIT_EDGE_NAME, sublattice_prefix
from covalent._shared_files.schemas.result import ResultSchema
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.electron import (
    Electron,
    _build_sublattice_graph,
    filter_null_metadata,
    get_serialized_function_str,
)
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import TransportableObject, encode_metadata
from covalent.executor.executor_plugins.local import LocalExecutor


@ct.electron
def task_1(a):
    import time

    time.sleep(3)
    return a**2


@ct.electron
def task_2(x, y):
    return x * y


@ct.electron
def task_3(b):
    return b**3


@ct.lattice
def workflow():
    res_1 = task_1(2)
    res_2 = task_2(res_1, 3)
    res_3 = ct.wait(task_3(5), res_1)

    return task_2(res_2, res_3)


@ct.lattice
def workflow_2():
    res_1 = task_1(2)
    res_2 = task_2(res_1, 3)
    res_3 = task_3(res_1)
    ct.wait(res_3, [res_1])

    return res_3


def test_build_sublattice_graph(mocker):
    """
    Test building a sublattice graph
    """
    dispatch_id = "test_build_sublattice_graph"

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    parent_metadata = {
        "executor": "parent_executor",
        "executor_data": {},
        "workflow_executor": "my_postprocessor",
        "workflow_executor_data": {},
        "hooks": {
            "deps": {"bash": None, "pip": None},
            "call_before": [],
            "call_after": [],
        },
        "triggers": "mock-trigger",
        "qelectron_data_exists": False,
        "results_dir": None,
    }
    mock_environ = {
        "COVALENT_DISPATCH_ID": dispatch_id,
        "COVALENT_DISPATCHER_URL": "http://localhost:48008",
    }

    mock_manifest = MagicMock()
    mock_manifest.json = MagicMock(return_value=dispatch_id)

    def mock_register(manifest, *args, **kwargs):
        return manifest

    mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register_manifest",
        mock_register,
    )

    mock_upload_assets = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.upload_assets",
    )

    mocker.patch("os.environ", mock_environ)

    json_manifest = _build_sublattice_graph(workflow, json.dumps(parent_metadata), 1)

    manifest = ResultSchema.parse_raw(json_manifest)

    mock_upload_assets.assert_called()

    assert len(manifest.lattice.transport_graph.nodes) == 3

    lat = manifest.lattice
    assert lat.metadata.executor == parent_metadata["executor"]
    assert lat.metadata.executor_data == parent_metadata["executor_data"]

    assert lat.metadata.workflow_executor == parent_metadata["workflow_executor"]
    assert lat.metadata.workflow_executor_data == parent_metadata["workflow_executor_data"]


def test_build_sublattice_graph_staging_uri(mocker):
    """Test that building a sublattice graph with staging uri."""

    dispatch_id = "test_build_sublattice_graph_staging_uri"

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    parent_metadata = {
        "executor": "parent_executor",
        "executor_data": {},
        "workflow_executor": "my_postprocessor",
        "workflow_executor_data": {},
        "hooks": {
            "deps": {"bash": None, "pip": None},
            "call_before": [],
            "call_after": [],
        },
        "triggers": "mock-trigger",
        "qelectron_data_exists": False,
        "results_dir": None,
    }

    with tempfile.TemporaryDirectory() as tmp_dir:
        mock_environ = {
            "COVALENT_DISPATCH_ID": dispatch_id,
            "COVALENT_STAGING_URI_PREFIX": f"file://{tmp_dir}",
        }
        mocker.patch("os.environ", mock_environ)
        json_manifest = _build_sublattice_graph(workflow, json.dumps(parent_metadata), 1)

        # Check that asset uris start with the staging prefix
        manifest = ResultSchema.model_validate_json(json_manifest)
        for key, asset in manifest.assets:
            if asset.size > 0:
                assert asset.uri.startswith(mock_environ["COVALENT_STAGING_URI_PREFIX"])

        for key, asset in manifest.lattice.assets:
            if asset.size > 0:
                assert asset.uri.startswith(mock_environ["COVALENT_STAGING_URI_PREFIX"])


def test_build_sublattice_graph_fallback(mocker):
    """
    Test falling back to monolithic sublattice dispatch
    """
    dispatch_id = "test_build_sublattice_graph"

    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    parent_metadata = {
        "executor": "parent_executor",
        "executor_data": {},
        "workflow_executor": "my_postprocessor",
        "workflow_executor_data": {},
        "hooks": {
            "deps": {"bash": None, "pip": None},
            "call_before": [],
            "call_after": [],
        },
        "triggers": "mock-trigger",
        "qelectron_data_exists": False,
        "results_dir": None,
    }

    # Omit the required environment variables
    mock_environ = {}

    mock_reg = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.register_manifest",
    )

    mock_upload_assets = mocker.patch(
        "covalent._dispatcher_plugins.local.LocalDispatcher.upload_assets",
    )

    mocker.patch("os.environ", mock_environ)

    json_lattice = _build_sublattice_graph(workflow, json.dumps(parent_metadata), 1)

    lattice = Lattice.deserialize_from_json(json_lattice)

    mock_reg.assert_not_called()
    mock_upload_assets.assert_not_called()

    assert list(lattice.transport_graph._graph.nodes) == list(range(3))
    for k in lattice.metadata.keys():
        # results_dir will be deprecated soon
        if k == "triggers":
            assert lattice.metadata[k] is None
        elif k != "results_dir":
            assert parent_metadata[k] == lattice.metadata[k]


def test_wait_for_building():
    """Test to check whether the graph is built correctly with `wait_for`."""

    workflow.build_graph()
    assert workflow.transport_graph.get_edge_data(0, 4)[0]["edge_name"] == WAIT_EDGE_NAME


def test_wait_for_post_processing():
    """Test to check post processing with `wait` works fine."""

    workflow.build_graph()
    with active_lattice_manager.claim(workflow):
        workflow.post_processing = True
        workflow.electron_outputs = [
            4,
            12,
            125,
            1500,
        ]
        assert workflow.workflow_function.get_deserialized()() == 1500


def test_wait_for_post_processing_when_returning_waiting_electron():
    """Test to check post processing with `wait` works fine when returning
    an electron with incoming wait_for edges"""

    workflow_2.build_graph()
    with active_lattice_manager.claim(workflow_2):
        workflow_2.post_processing = True
        workflow_2.electron_outputs = [
            4,
            12,
            64,
        ]
        assert workflow_2.workflow_function.get_deserialized()() == 64


def test_injected_inputs_are_not_in_tg():
    """Test that arguments to electrons injected by calldeps aren't
    added to the transport graph"""

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep])
    def task(x, y=0):
        return (x, y)

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(2)
    g = workflow.transport_graph._graph

    # Account for postprocessing node
    assert list(g.nodes) == [0, 1, 2]
    assert set(g.edges) == {(1, 0, 0), (0, 2, 0), (0, 2, 1)}


def test_metadata_in_electron_list():
    """Test if metadata of the created electron list apart from executor is set to default values"""

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep], executor=LocalExecutor())
    def task(x, y=0):
        return (x, y)

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph([2])

    task_metadata = workflow.transport_graph.get_node_value(0, "metadata")
    e_list_metadata = workflow.transport_graph.get_node_value(1, "metadata")

    assert "call_before" not in e_list_metadata["hooks"]
    assert "call_after" not in e_list_metadata["hooks"]

    assert e_list_metadata["executor"] == task_metadata["executor"]


def test_electron_metadata_is_serialized_early():
    """Test that electron metadata is JSON-serialized before it is
    stored in the graph.

    This checks that `constraints` are already serialized before being
    passed to the `decorator_electron` closure.

    """

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.electron(call_before=[calldep], executor=LocalExecutor())
    def task(x):
        return x

    @ct.lattice(workflow_executor=LocalExecutor())
    def workflow(x):
        return task(x)

    workflow.build_graph(2)
    node_0_metadata = workflow.transport_graph.get_node_value(0, "metadata")
    assert node_0_metadata == encode_metadata(node_0_metadata)
    node_1_metadata = workflow.transport_graph.get_node_value(1, "metadata")
    assert node_1_metadata == encode_metadata(node_1_metadata)


def test_autogen_list_electrons():
    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph([5, 7])

    g = workflow.transport_graph._graph

    # Account for postprocessing node
    assert list(g.nodes) == [0, 1, 2, 3, 4]
    fn = g.nodes[1]["function"].get_deserialized()
    assert fn(2, 5, 7) == [2, 5, 7]

    assert g.nodes[2]["value"].get_deserialized() == 5
    assert g.nodes[3]["value"].get_deserialized() == 7
    assert set(g.edges) == {
        (1, 0, 0),
        (2, 1, 0),
        (3, 1, 0),
        (0, 4, 0),
        (0, 4, 1),
        (1, 4, 0),
    }


def test_autogen_dict_electrons():
    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph({"x": 5, "y": 7})

    g = workflow.transport_graph._graph

    # Account for postprocessing node
    assert list(g.nodes) == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    fn = g.nodes[1]["function"].get_deserialized()
    assert fn(["x", "y", "z"], [2, 5, 7]) == {"x": 2, "y": 5, "z": 7}
    fn = g.nodes[2]["function"].get_deserialized()
    assert fn("x", "y") == ["x", "y"]
    keys = [g.nodes[3]["value"].get_deserialized(), g.nodes[4]["value"].get_deserialized()]
    fn = g.nodes[5]["function"].get_deserialized()
    assert fn(2, 3) == [2, 3]
    vals = [g.nodes[6]["value"].get_deserialized(), g.nodes[7]["value"].get_deserialized()]
    assert keys == ["x", "y"]
    assert vals == [5, 7]
    assert set(g.edges) == {
        (1, 0, 0),
        (2, 1, 0),
        (3, 2, 0),
        (4, 2, 0),
        (5, 1, 0),
        (6, 5, 0),
        (7, 5, 0),
        (0, 8, 0),
        (0, 8, 1),
        (1, 8, 0),
        (2, 8, 0),
        (5, 8, 0),
    }


def test_as_transportable_dict():
    """Test the get transportable electron function."""

    @ct.electron
    def test_func(a):
        return a

    mock_metadata = {"a": 1, "b": 2, "c": None}
    # Construct bound electron, i.e. electron with non-null function and node_id
    electron = Electron(function=test_func, node_id=1, metadata=mock_metadata)
    transportable_electron = electron.as_transportable_dict

    assert transportable_electron["name"] == "test_func"
    assert transportable_electron["metadata"] == filter_null_metadata(mock_metadata)
    assert transportable_electron["function_string"] == get_serialized_function_str(test_func)
    assert TransportableObject(test_func).to_dict() == transportable_electron["function"]


def test_call_sublattice():
    """Test the sublattice logic when the __call__ method is invoked."""

    le = LocalExecutor()
    bash_dep = ct.DepsBash("apt install rustc cargo")

    @ct.lattice(executor=le, workflow_executor="dask", deps_bash=bash_dep)
    def mock_workflow(x):
        return sublattice(x)

    @ct.electron
    def mock_task(x):
        return x

    @ct.electron
    @ct.lattice
    def sublattice(x):
        return mock_task(x)

    with active_lattice_manager.claim(mock_workflow):
        bound_electron = sublattice()
        assert bound_electron.metadata["executor"] == "dask"
        assert bound_electron.metadata["executor_data"] == {}
        assert bound_electron.metadata["hooks"]["deps"]["bash"] == bash_dep.to_dict()
        for _, node_data in mock_workflow.transport_graph._graph.nodes(data=True):
            if node_data["name"].startswith(sublattice_prefix):
                assert "mock_task" in node_data["function_string"]
                assert "sublattice" in node_data["function_string"]
                assert (
                    node_data["function"].get_deserialized().__name__ == "_build_sublattice_graph"
                )


@pytest.mark.parametrize("task_packing", ["true", "false"])
def test_electron_auto_task_groups(task_packing):
    @ct.electron
    def task(arr: list):
        return sum(arr)

    @ct.electron
    @ct.lattice
    def sublattice(x):
        return task(x)

    @ct.lattice
    def workflow(x):
        return sublattice(x)

    ct.set_config("sdk.task_packing", task_packing)
    workflow.build_graph([[1, 2], 3])
    tg = workflow.transport_graph

    if task_packing == "true":
        assert all(tg.get_node_value(i, "task_group_id") == 0 for i in [0, 3, 4])
        assert all(tg.get_node_value(i, "task_group_id") == i for i in [1, 2, 5, 6, 7, 8])
    else:
        assert all(tg.get_node_value(i, "task_group_id") == i for i in range(9))


@pytest.mark.parametrize("task_packing", ["true", "false"])
def test_electron_get_attr(task_packing):
    class Point:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    @ct.electron
    def create_point():
        return Point(3, 4)

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow():
        point = create_point()
        return add(point.x, point.y)

    ct.set_config("sdk.task_packing", task_packing)
    workflow.build_graph()
    tg = workflow.transport_graph

    # TG:
    # 0: point
    # 1: point.__getattr__
    # 2: "x"
    # 3: point.__getattr__
    # 4: "y"
    # 5: add
    # 6: "postprocess"

    if task_packing == "true":
        point_electron_gid = tg.get_node_value(0, "task_group_id")
        getitem_x_gid = tg.get_node_value(1, "task_group_id")
        getitem_y_gid = tg.get_node_value(3, "task_group_id")
        assert point_electron_gid == 0
        assert getitem_x_gid == point_electron_gid
        assert getitem_y_gid == point_electron_gid
        assert all(tg.get_node_value(i, "task_group_id") == i for i in [2, 4, 5, 6])
    else:
        assert all(tg.get_node_value(i, "task_group_id") == i for i in range(7))


@pytest.mark.parametrize("task_packing", ["true", "false"])
def test_electron_auto_task_groups_getitem(task_packing):
    """Test task packing with __getitem__"""

    @ct.electron
    def create_array():
        return [3, 4]

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow():
        arr = create_array()
        return add(arr[0], arr[1])

    ct.set_config("sdk.task_packing", task_packing)
    workflow.build_graph()
    tg = workflow.transport_graph

    # TG:
    # 0: arr
    # 1: arr.__getitem__
    # 2: 0
    # 3: arr.__getitem__
    # 4: 1
    # 5: add
    # 6: "postprocess"

    if task_packing == "true":
        arr_electron_gid = tg.get_node_value(0, "task_group_id")
        getitem_x_gid = tg.get_node_value(1, "task_group_id")
        getitem_y_gid = tg.get_node_value(3, "task_group_id")
        assert arr_electron_gid == 0
        assert getitem_x_gid == arr_electron_gid
        assert getitem_y_gid == arr_electron_gid
        assert all(tg.get_node_value(i, "task_group_id") == i for i in [2, 4, 5, 6])
    else:
        assert all(tg.get_node_value(i, "task_group_id") == i for i in range(7))


@pytest.mark.parametrize("task_packing", ["true", "false"])
def test_electron_auto_task_groups_iter(task_packing):
    """Test task packing with __iter__"""

    @ct.electron
    def create_tuple():
        return (3, 4)

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow():
        tup = create_tuple()
        x, y = tup
        return add(x, y)

    ct.set_config("sdk.task_packing", task_packing)
    workflow.build_graph()
    tg = workflow.transport_graph

    # TG:
    # 0: tup
    # 1: tup.__getitem__
    # 2: 0
    # 3: tup.__getitem__
    # 4: 1
    # 5: add
    # 6: "postprocess"

    if task_packing == "true":
        tup_electron_gid = tg.get_node_value(0, "task_group_id")
        getitem_x_gid = tg.get_node_value(1, "task_group_id")
        getitem_y_gid = tg.get_node_value(3, "task_group_id")
        assert tup_electron_gid == 0
        assert getitem_x_gid == tup_electron_gid
        assert getitem_y_gid == tup_electron_gid
        assert all(tg.get_node_value(i, "task_group_id") == i for i in [2, 4, 5, 6])
    else:
        assert all(tg.get_node_value(i, "task_group_id") == i for i in range(7))


def test_electron_executor_property():
    """
    Test that the executor property assignment
    of an electron works as expected.
    """

    @ct.electron
    def mock_task():
        pass

    mock_encoded_metadata = encode_metadata({"executor": LocalExecutor()})

    mock_task_electron = mock_task.electron_object

    # If string is passed
    mock_task_electron.executor = "mock"
    assert mock_task_electron.metadata["executor"] == "mock"

    # If executor object is passed
    mock_task_electron.executor = LocalExecutor()
    assert mock_task_electron.metadata["executor"] == mock_encoded_metadata["executor"]
    assert mock_task_electron.metadata["executor_data"] == mock_encoded_metadata["executor_data"]


def test_replace_electrons():
    """Test the logic in __call__ to replace electrons."""

    @ct.electron
    def task(x):
        return x**2

    @ct.electron
    def replacement_task(x):
        return x**3

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow._replace_electrons = {"task": replacement_task}
    workflow.build_graph(3)
    del workflow.__dict__["_replace_electrons"]

    func = workflow.transport_graph.get_node_value(0, "function")
    assert func.get_deserialized()(3) == 27
    assert (
        workflow.transport_graph.get_node_value(0, "status") == RESULT_STATUS.PENDING_REPLACEMENT
    )


def test_electron_pow_method(mocker):
    mock_electron_get_op_function = mocker.patch.object(
        Electron, "get_op_function", return_value=Electron
    )

    @ct.electron
    def g(x):
        return 42 * x

    @ct.lattice
    def workflow(x):
        res = g(x)
        return res**2

    workflow.build_graph(2)

    mock_electron_get_op_function.assert_called_with(ANY, 2, "**")


@pytest.mark.parametrize(
    "module_inputs",
    [
        "isort",
        isort,
        ct.DepsModule("isort"),
        ["isort", "flake8"],
        [isort, flake8],
        [ct.DepsModule("isort"), ct.DepsModule("flake8")],
    ],
)
def test_deps_modules_are_added(module_inputs):
    """Test that deps modules are added to the lattice metadata."""

    @ct.electron(deps_module=module_inputs)
    def task(x):
        return x

    # Making sure all kinds of inputs are converted to DepsModule
    # and then to its transportable form of a dictionary
    for cb in task.electron_object.metadata["hooks"]["call_before"]:
        assert cb["short_name"] == "depsmodule"
        assert cb["attributes"]["pickled_module"]["type"] == "TransportableObject"
