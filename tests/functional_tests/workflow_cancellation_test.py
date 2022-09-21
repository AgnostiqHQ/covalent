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
from covalent._shared_files.config import CMType, get_config
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
async def test_result_cancel_local_executor(event_loop):
    """Integration test for Result._cancel with local executor"""

    import asyncio
    import time

    from covalent.executor import LocalExecutor

    local_exec = LocalExecutor().get_shared_instance()

    @ct.electron(executor=local_exec)
    def sleeping_task(delay):
        import time

        time.sleep(delay)
        print("Slept for {delay} seconds")
        return delay

    @ct.lattice
    def workflow(x):
        res = sleeping_task(x)
        res2 = sleeping_task(res)
        return 1

    sleeping_time = 4
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
    assert local_exec.instance_id in cache.id_instance_map
    assert et - st < 2 * sleeping_time

    assert result_object._status == Result.CANCELLED
    loop = asyncio.get_running_loop()
    print("Scheduled tasks", loop._scheduled)


def test_cancel_endpoint():
    """End-to-end test of /api/cancel"""
    import time

    import requests

    @ct.electron
    def sleeping_task(delay):
        import time

        time.sleep(delay)
        print("Slept for {delay} seconds")
        return delay

    @ct.lattice
    def workflow(x):
        res = sleeping_task(x)
        res2 = sleeping_task(res)
        return 1

    dispatch_id = ct.dispatch(workflow)(8)
    time.sleep(0.2)

    server_ip = str(get_config(CMType.CLIENT, "server.address"))
    server_port = str(get_config(CMType.CLIENT, "server.port"))
    cancel_url = "http://" + server_ip + ":" + server_port + "/api/cancel"

    r = requests.post(cancel_url, data=dispatch_id)
    expected_cancel_msg = f"Dispatch {dispatch_id} cancelled."
    r.raise_for_status()
    assert r.content.decode("utf-8").strip().replace('"', "") == expected_cancel_msg

    result = ct.get_result(dispatch_id, wait=True)
    assert result.status == ct.status.CANCELLED


def test_dummy_end():
    """Hack to prevent pytest from prematurely closing the event loop
    in pytest_fixture_post_finalizer. This should be the last test
    executed.
    """

    asyncio.run(asyncio.sleep(0.1))
