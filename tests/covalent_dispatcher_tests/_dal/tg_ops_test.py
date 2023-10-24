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

"""Unit tests for transport graph operations module."""

import types
from unittest.mock import MagicMock

import pytest

from covalent._shared_files.util_classes import RESULT_STATUS
from covalent_dispatcher._dal.asset import StorageType
from covalent_dispatcher._dal.tg_ops import TransportGraphOps, _TransportGraph


def add(x, y):
    return x + y


def multiply(x, y):
    return x * y


def identity(x):
    return x


# Mocks
def set_node_value(self, node_id, k, v):
    self._graph.nodes[node_id][k] = v


def get_node_value(self, node_id, k):
    return self._graph.nodes[node_id][k]


@pytest.fixture
def tg():
    """Transport graph operations fixture, suitable for pure nx queries"""

    tg = _TransportGraph(lattice_id=1)
    tg.get_node_value = types.MethodType(get_node_value, tg)
    tg.set_node_value = types.MethodType(set_node_value, tg)

    tg._graph.add_node(
        0,
        name="add",
        function=add,
        metadata={"0-mock-key": "0-mock-value"},
        status=RESULT_STATUS.NEW_OBJECT,
    )
    tg._graph.add_node(
        1,
        name="multiply",
        function=multiply,
        metadata={"1-mock-key": "1-mock-value"},
        status=RESULT_STATUS.NEW_OBJECT,
    )
    tg._graph.add_node(
        2,
        name="identity",
        function=identity,
        metadata={"2-mock-key": "2-mock-value"},
        status=RESULT_STATUS.NEW_OBJECT,
    )
    return tg


@pytest.fixture
def tg_2():
    """Transport graph operations fixture - different from tg."""
    tg_2 = _TransportGraph(lattice_id=2)
    tg_2.get_node_value = types.MethodType(get_node_value, tg_2)
    tg_2.set_node_value = types.MethodType(set_node_value, tg_2)

    tg_2._graph.add_node(
        0,
        name="not-add",
        function=add,
        metadata={"0- mock-key": "0-mock-value"},
        status=RESULT_STATUS.NEW_OBJECT,
    )
    tg_2._graph.add_node(
        1,
        name="multiply",
        function=multiply,
        metadata={"1- mock-key": "1-mock-value"},
        status=RESULT_STATUS.NEW_OBJECT,
    )
    tg_2._graph.add_node(
        2,
        name="identity",
        function=identity,
        metadata={"2- mock-key": "2-mock-value"},
        status=RESULT_STATUS.NEW_OBJECT,
    )
    return tg_2


@pytest.fixture
def tg_ops(tg):
    """Transport graph operations fixture."""
    return TransportGraphOps(tg)


def test_init(tg):
    """Test initialization of transport graph operations."""
    tg_ops = TransportGraphOps(tg)
    assert tg_ops.tg == tg
    assert tg_ops._status_map == {1: True, -1: False}


def test_flag_successors_no_successors(tg, tg_ops):
    """Test flagging successors of a node."""
    node_statuses = {0: 1, 1: 1, 2: 1}
    tg_ops._flag_successors(tg._graph, node_statuses=node_statuses, starting_node=0)
    assert node_statuses == {0: -1, 1: 1, 2: 1}


@pytest.mark.parametrize(
    "n_1,n_2,n_start,label,new_statuses",
    [
        (0, 1, 0, "01", {0: -1, 1: -1, 2: 1}),
        (1, 2, 0, "12", {0: -1, 1: 1, 2: 1}),
        (1, 2, 1, "12", {0: 1, 1: -1, 2: -1}),
        (1, 2, 2, "12", {0: 1, 1: 1, 2: -1}),
    ],
)
def test_flag_successors_with_one_successors(tg, tg_ops, n_1, n_2, n_start, label, new_statuses):
    """Test flagging successors of a node."""
    tg._graph.add_edge(n_1, n_2, label)
    node_statuses = {0: 1, 1: 1, 2: 1}
    tg_ops._flag_successors(tg._graph, node_statuses=node_statuses, starting_node=n_start)
    assert node_statuses == new_statuses


@pytest.mark.parametrize(
    "n_1,n_2,n_3,n_4,label_1,label_2,n_start,new_statuses",
    [
        (0, 1, 1, 2, "01", "12", 0, {0: -1, 1: -1, 2: -1}),
        (0, 1, 0, 2, "01", "02", 0, {0: -1, 1: -1, 2: -1}),
        (0, 1, 0, 2, "01", "12", 1, {0: 1, 1: -1, 2: 1}),
    ],
)
def test_flag_successors_with_successors_3(
    tg, tg_ops, n_1, n_2, n_3, n_4, label_1, n_start, label_2, new_statuses
):
    """Test flagging successors of a node."""
    tg._graph.add_edge(n_1, n_2, label_1)
    tg._graph.add_edge(n_3, n_4, label_2)
    node_statuses = {0: 1, 1: 1, 2: 1}
    tg_ops._flag_successors(tg._graph, node_statuses=node_statuses, starting_node=n_start)
    assert node_statuses == new_statuses


def test_is_same_node_true(tg, tg_ops):
    """Test the is same node method."""
    assert tg_ops.is_same_node(tg._graph, tg._graph, 0) is True
    assert tg_ops.is_same_node(tg._graph, tg._graph, 1) is True


def test_is_same_node_false(tg, tg_ops):
    """Test the is same node method."""
    tg_2 = _TransportGraph(lattice_id=2)
    tg_2._graph.add_node(
        0, name="multiply", function=add, metadata={"0- mock-key": "0-mock-value"}
    )
    assert tg_ops.is_same_node(tg._graph, tg_2._graph, 0) is False


def test_is_same_edge_attributes_true(tg, tg_ops):
    """Test the is same edge attributes method."""
    tg._graph.add_edge(0, 1, edge_name="01", kwargs={"x": 1, "y": 2})
    assert tg_ops.is_same_edge_attributes(tg._graph, tg._graph, 0, 1) is True


def test_is_same_edge_attributes_false(tg, tg_ops):
    """Test the is same edge attributes method."""
    tg._graph.add_edge(0, 1, edge_name="01", kwargs={"x": 1, "y": 2})

    tg_2 = _TransportGraph(lattice_id=2)
    tg_2._graph.add_node(0, name="add", function=add, metadata={"0- mock-key": "0-mock-value"})
    tg_2._graph.add_node(
        1, name="multiply", function=multiply, metadata={"1- mock-key": "1-mock-value"}
    )
    tg_2._graph.add_node(
        2, name="identity", function=identity, metadata={"2- mock-key": "2-mock-value"}
    )
    tg_2._graph.add_edge(0, 1, edge_name="01", kwargs={"x": 1})

    assert tg_ops.is_same_edge_attributes(tg._graph, tg_2._graph, 0, 1) is False


def test_copy_nodes_from(tg, mocker):
    """Test the node copying method."""

    def replacement(x):
        return x + 1

    # mock get/set_node_value, get_asset

    mock_old_asset = MagicMock()
    mock_new_asset = MagicMock()
    mock_old_asset.storage_type = StorageType.LOCAL
    mock_old_asset.storage_path = "/tmp"
    mock_old_asset.object_key = "result.pkl"
    mock_new_asset.storage_type = StorageType.LOCAL
    mock_new_asset.storage_path = "/tmp"
    mock_new_asset.object_key = "result_new.pkl"

    mock_old_node = MagicMock()
    mock_new_node = MagicMock()
    mock_old_node.get_asset = MagicMock(return_value=mock_old_asset)
    mock_new_node.get_asset = MagicMock(return_value=mock_new_asset)

    MOCK_META_KEYS = {"name"}
    MOCK_ASSET_KEYS = {"function"}
    mocker.patch("covalent_dispatcher._dal.tg_ops.METADATA_KEYS", MOCK_META_KEYS)
    mocker.patch("covalent_dispatcher._dal.tg_ops.ASSET_KEYS", MOCK_ASSET_KEYS)

    mock_copy_asset = mocker.patch("covalent_dispatcher._dal.tg_ops.copy_asset")
    mock_copy_asset_meta = mocker.patch("covalent_dispatcher._dal.tg_ops.copy_asset_meta")

    tg_new = _TransportGraph(lattice_id=2)

    tg.get_node = MagicMock(return_value=mock_old_node)
    tg_new.get_node = MagicMock(return_value=mock_new_node)

    tg_new.get_node_value = types.MethodType(get_node_value, tg_new)
    tg_new.set_node_value = types.MethodType(set_node_value, tg_new)

    tg_new._graph.add_node(
        0,
        name="replacement",
        function=replacement,
        status=RESULT_STATUS.COMPLETED,
        metadata={"0-mock-key": "0-mock-value"},
    )
    tg_new._graph.add_node(
        1,
        name="multiply",
        function=multiply,
        status=RESULT_STATUS.NEW_OBJECT,
        metadata={"1-mock-key": "1-mock-value"},
    )
    tg_new._graph.add_node(
        2,
        name="replacement",
        function=replacement,
        status=RESULT_STATUS.COMPLETED,
        metadata={"2-mock-key": "2-mock-value"},
    )

    tg_ops = TransportGraphOps(tg)

    tg_ops.copy_nodes_from(tg_new, [0, 2])
    assert (
        tg_ops.tg._graph.nodes(data=True)[0]["name"]
        == tg_ops.tg._graph.nodes(data=True)[2]["name"]
        == "replacement"
    )

    assert tg_ops.tg._graph.nodes[1]["name"] == "multiply"
    assert tg_ops.tg._graph.nodes(data=True)[2]["name"] == "replacement"

    assert mock_copy_asset.call_count == 2
    assert mock_copy_asset_meta.call_count == 2


def test_max_cbms(tg_ops):
    """Test method for determining a largest cbms"""
    import networkx as nx

    A = nx.MultiDiGraph()
    B = nx.MultiDiGraph()
    C = nx.MultiDiGraph()
    D = nx.MultiDiGraph()

    #    0     5  6
    #  /  \
    # 1    2
    A.add_edge(0, 1)
    A.add_edge(0, 2)
    A.nodes[1]["color"] = "red"
    A.add_node(5)
    A.add_node(6)

    #    0     5
    #  /  \\
    # 1    2
    B.add_edge(0, 1)
    B.add_edge(0, 2)
    B.add_edge(0, 2)
    B.nodes[1]["color"] = "black"
    B.add_node(5)

    #    0    3
    #  /  \  /
    # 1    2
    C.add_edge(0, 1)
    C.add_edge(0, 2)
    C.add_edge(3, 2)

    #    0    3
    #  /  \  /
    # 1    2
    #     /
    #   4
    D.add_edge(0, 1)
    D.add_edge(0, 2)
    D.add_edge(3, 2)
    D.add_edge(2, 4)

    A_node_status, B_node_status = tg_ops._max_cbms(A, B)
    assert A_node_status == {0: True, 1: False, 2: False, 5: True, 6: False}
    assert B_node_status == {0: True, 1: False, 2: False, 5: True}

    A_node_status, C_node_status = tg_ops._max_cbms(A, C)
    assert A_node_status == {0: True, 1: False, 2: False, 5: False, 6: False}
    assert C_node_status == {0: True, 1: False, 2: False, 3: False}

    C_node_status, D_node_status = tg_ops._max_cbms(C, D)
    assert C_node_status == {0: True, 1: True, 2: True, 3: True}
    assert D_node_status == {0: True, 1: True, 2: True, 3: True, 4: False}


def test_cmp_name_and_pval_true(tg, tg_ops):
    """Test the name and parameter value comparison method."""
    assert tg_ops._cmp_name_and_pval(tg._graph, tg._graph, 0) is True


def test_cmp_name_and_pval_false(tg, tg_2, tg_ops):
    """Test the name and parameter value comparison method."""
    assert tg_ops._cmp_name_and_pval(tg._graph, tg_2._graph, 0) is False


def test_cmp_name_and_pval_pending_replacement(tg, tg_ops):
    """Test the name and parameter value comparison method."""
    import copy

    tg_3 = copy.deepcopy(tg)
    tg_3.set_node_value(0, "status", RESULT_STATUS.PENDING_REPLACEMENT)
    assert tg_ops._cmp_name_and_pval(tg._graph, tg_3._graph, 0) is False


def test_get_reusable_nodes(mocker, tg, tg_2):
    """Test the get reusable nodes method."""
    max_cbms_mock = mocker.patch(
        "covalent_dispatcher._dal.tg_ops.TransportGraphOps._max_cbms",
        return_value=({"mock-key-A": "mock-value-A"}, {"mock-key-B": "mock-value-B"}),
    )
    mock_old_asset = MagicMock()
    mock_new_asset = MagicMock()
    mock_old_asset.storage_type = StorageType.LOCAL
    mock_old_asset.storage_path = "/tmp"
    mock_old_asset.object_key = "value.pkl"
    mock_old_asset.meta = {"digest": "24af"}
    mock_new_asset.storage_type = StorageType.LOCAL
    mock_new_asset.storage_path = "/tmp"
    mock_new_asset.object_key = "value.pkl"
    mock_new_asset.meta = {"digest": "24af"}

    mock_old_node = MagicMock()
    mock_new_node = MagicMock()
    mock_old_node.get_asset = MagicMock(return_value=mock_old_asset)
    mock_new_node.get_asset = MagicMock(return_value=mock_new_asset)

    tg.get_node = MagicMock(return_value=mock_old_node)
    tg_2.get_node = MagicMock(return_value=mock_new_node)

    tg_ops = TransportGraphOps(tg)
    reusable_nodes = tg_ops.get_reusable_nodes(tg_2)
    assert reusable_nodes == ["mock-key-A"]
    max_cbms_mock.assert_called_once()


def test_get_diff_nodes_integration_test(tg, tg_2):
    """Test the get reusable nodes method."""

    mock_old_asset = MagicMock()
    mock_new_asset = MagicMock()
    mock_old_asset.storage_type = StorageType.LOCAL
    mock_old_asset.storage_path = "/tmp"
    mock_old_asset.object_key = "value.pkl"
    mock_old_asset.__dict__.update({"digest": "24af"})
    mock_new_asset.storage_type = StorageType.LOCAL
    mock_new_asset.storage_path = "/tmp"
    mock_new_asset.object_key = "value.pkl"
    mock_new_asset.__dict__.update({"digest": "24af"})

    mock_old_node = MagicMock()
    mock_new_node = MagicMock()
    mock_old_node.get_asset = MagicMock(return_value=mock_old_asset)
    mock_new_node.get_asset = MagicMock(return_value=mock_new_asset)

    tg.get_node = MagicMock(return_value=mock_old_node)
    tg_2.get_node = MagicMock(return_value=mock_new_node)

    tg_ops = TransportGraphOps(tg)

    reusable_nodes = tg_ops.get_reusable_nodes(tg_2)
    assert reusable_nodes == [1, 2]


def test_reset_node(tg):
    tg.set_node_value(0, "status", RESULT_STATUS.PENDING_REPLACEMENT)

    tg_ops = TransportGraphOps(tg)
    tg_ops.reset_nodes()
    assert tg.get_node_value(0, "status") == RESULT_STATUS.NEW_OBJECT
    assert tg.get_node_value(0, "start_time") is None
    assert tg.get_node_value(0, "end_time") is None
