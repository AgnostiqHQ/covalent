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
Tests for executor runtime utils
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

import covalent as ct
from covalent._results_manager import Result
from covalent._workflow.lattice import Lattice
from covalent.executor._runtime.utils import ExecutorCache

TEST_RESULTS_DIR = "/tmp/results"


def get_mock_result() -> Result:
    """Construct a mock result object corresponding to a lattice."""

    import sys

    @ct.electron(executor="local")
    def task(x):
        print(f"stdout: {x}")
        print("Error!", file=sys.stderr)
        return x

    @ct.lattice(results_dir=TEST_RESULTS_DIR)
    def pipeline(x):
        res1 = task(x)
        res2 = task(res1)
        return res2

    pipeline.build_graph(x="absolute")
    received_workflow = Lattice.deserialize_from_json(pipeline.serialize_to_json())
    result_object = Result(
        received_workflow, pipeline.metadata["results_dir"], "pipeline_workflow"
    )

    return result_object


def test_executor_cache_init(mocker):
    result_object = get_mock_result()
    mock_init = mocker.patch(
        "covalent.executor._runtime.utils.ExecutorCache.initialize_from_result_object"
    )
    cache = ExecutorCache(result_object)
    mock_init.assert_called_once_with(result_object)


def test_executor_cache_initialize_from_result():
    """Test ExecuterCache initialize correctly counts the tasks assigned
    to each cached executor"""

    from covalent._workflow.lattice import Lattice
    from covalent.executor import LocalExecutor

    le1 = LocalExecutor().get_shared_instance()
    le2 = LocalExecutor().get_shared_instance()
    le3 = LocalExecutor()

    id_1 = le1.instance_id
    id_2 = le2.instance_id

    @ct.electron(executor=le1)
    def task_1(x):
        return x

    @ct.electron(executor=le2)
    def task_2(x):
        return x

    @ct.electron(executor=le2)
    def task_3(x):
        return x

    @ct.electron(executor="local")
    def task_4(x):
        return x

    @ct.lattice(workflow_executor="local")
    def workflow_1(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res4

    @ct.lattice(workflow_executor=le2)
    def workflow_2(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res4

    @ct.lattice(workflow_executor=le3)
    def workflow_3(x):
        res1 = task_1(x)
        res2 = task_2(res1)
        res3 = task_3(res2)
        res4 = task_4(res3)
        return res4

    @ct.lattice(workflow_executor=le2)
    def workflow_4(x):
        return task_1(x)

    workflow_1.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_1.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    tg = received_lattice.transport_graph

    task4_eid = tg._graph.nodes[4]["metadata"]["executor_data"]["attributes"]["instance_id"]
    workflow_eid = received_lattice.metadata["workflow_executor_data"]["attributes"]["instance_id"]
    assert id_1 in cache.id_instance_map.keys()
    assert id_2 in cache.id_instance_map.keys()
    assert task4_eid in cache.id_instance_map.keys()
    assert workflow_eid in cache.id_instance_map.keys()
    assert len(cache.id_instance_map.keys()) == 4
    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 2
    assert cache.tasks_per_instance[task4_eid] == 1
    assert cache.tasks_per_instance[workflow_eid] == 1

    # Test using shared workflow executor instance
    workflow_2.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_2.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 3

    # Test using exclusive workflow executor instance
    workflow_3.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_3.serialize_to_json())
    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 2

    # Test using workflow executor instance not shared by any other tasks
    workflow_4.build_graph(5)
    received_lattice = Lattice.deserialize_from_json(workflow_4.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    cache = ExecutorCache()
    cache.initialize_from_result_object(result_object)

    assert cache.tasks_per_instance[id_1] == 1
    assert cache.tasks_per_instance[id_2] == 1


@pytest.mark.asyncio
async def test_executor_cache_finalize():
    """Test `ExecutorCache.finalize()`"""

    from covalent.executor import DaskExecutor, LocalExecutor

    le = LocalExecutor().get_shared_instance()
    de = DaskExecutor("tcp://127.0.0.1:30000").get_shared_instance()

    le.teardown = MagicMock()
    de.teardown = AsyncMock()

    cache = ExecutorCache()
    cache.id_instance_map[le.instance_id] = le
    cache.id_instance_map[de.instance_id] = de

    await cache.finalize_executors()

    le.teardown.assert_called_once()
    de.teardown.assert_awaited_once()
