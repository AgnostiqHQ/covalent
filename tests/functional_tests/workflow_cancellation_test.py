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

import asyncio

import pytest

import covalent as ct
from covalent._data_store.datastore import DataStore
from covalent._results_manager.result import Result, initialize_result_object
from covalent_dispatcher._core.execution import run_workflow

TEST_RESULTS_DIR = "/tmp/results"


# Hack to prevent pytest from prematurely closing the asyncio event loop
@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


@pytest.mark.asyncio
async def test_result_cancel_dask_executor(event_loop):
    """Integration test for Result._cancel with dask executor"""

    import asyncio
    import time

    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    lc = LocalCluster()
    dask_exec = DaskExecutor(lc.scheduler_address).get_shared_instance()

    @ct.electron(executor=dask_exec)
    def sleeping_task(delay):
        import time

        time.sleep(delay)
        print("Slept for {delay} seconds")

    @ct.lattice
    def workflow(x):
        sleeping_task(x)
        return 1

    sleeping_time = 15
    workflow.build_graph(sleeping_time)

    json_lattice = workflow.serialize_to_json()
    result_object = initialize_result_object(json_lattice)

    st = time.time()
    fut = asyncio.create_task(run_workflow(result_object))
    await asyncio.sleep(0.1)
    await result_object._cancel()
    await fut
    et = time.time()

    cache = result_object._get_executor_cache()
    assert dask_exec.instance_id in cache.id_instance_map
    assert et - st < sleeping_time

    assert result_object._status == Result.CANCELLED
    loop = asyncio.get_running_loop()
    print("Scheduled tasks", loop._scheduled)


def test_dummy_end():
    """Hack to prevent pytest from prematurely closing the event loop
    in pytest_fixture_post_finalizer. This should be the last test
    executed.
    """

    asyncio.run(asyncio.sleep(0.1))
