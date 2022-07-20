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

import pytest
import asyncio
import time
import dask.system
from dask.distributed import LocalCluster
from distributed.comm import parse_address, unparse_address
from covalent_dispatcher._service.app_dask import DaskAdminWorker

from covalent_dispatcher._cli.service import (
    _get_cluster_status,
    _get_cluster_size,
    _get_cluster_info,
    _get_cluster_address,
    _cluster_restart,
    _cluster_scale
)

@pytest.fixture(scope="module")
def test_cluster():
    cluster = LocalCluster()
    yield cluster
    cluster.close()

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def admin_worker_addr(test_cluster):
    admin_host = "127.0.0.1"
    admin_port = 9000
    uri = unparse_address("tcp", f"{admin_host}:{admin_port}")
    admin_worker = DaskAdminWorker(cluster = test_cluster,
                        admin_host = admin_host,
                        admin_port = admin_port)
    admin_worker.daemon = True
    admin_worker.start()
    yield uri


@pytest.mark.asyncio
async def test_cluster_size_cli(test_cluster, admin_worker_addr, event_loop):
    """
    Assert covalent cluster size is equal to the default value
    """
    asyncio.set_event_loop(event_loop)
    result = await _get_cluster_size(admin_worker_addr)
    assert int(result) == len(test_cluster.workers)


@pytest.mark.asyncio
async def test_cluster_status_cli(admin_worker_addr, event_loop):
    """
    Assert cluster status CLI for default number of workers in the cluster
    """
    asyncio.set_event_loop(event_loop)
    response = await _get_cluster_status(admin_worker_addr)
    print(type(response))
    expected = {}
    expected["scheduler"] = "running"
    for i in range(dask.system.CPU_COUNT):
        expected[f"worker-{i}"] = "running"

    assert expected == response


@pytest.mark.asyncio
async def test_cluster_info_cli(admin_worker_addr, event_loop):
    """
    Test cluster info CLI for default number of workers, memory and threads per
    worker
    """
    asyncio.set_event_loop(event_loop)
    expected_keys = ["type", "id", "address", "services", "started", "workers"]
    worker_info_expected_keys = [
        "type",
        "id",
        "host",
        "resources",
        "local_directory",
        "name",
        "nthreads",
        "memory_limit",
        "last_seen",
        "services",
        "metrics",
        "status",
        "nanny",
    ]
    response = await _get_cluster_info(admin_worker_addr)
    assert list(response.keys()) == expected_keys
    assert len(response["workers"]) == dask.system.CPU_COUNT

    # Check the keys match for each worker in the cluster
    for _, value in response["workers"].items():
        assert list(value.keys()) == worker_info_expected_keys


@pytest.mark.asyncio
async def test_cluster_address_cli(admin_worker_addr, event_loop):
    """
    Test cluster address CLI
    """
    asyncio.set_event_loop(event_loop)
    expected_protocol = "tcp"
    expected_host = "127.0.0.1"

    response = await _get_cluster_address(admin_worker_addr)

    assert list(response.keys()) == ["scheduler", "workers"]
    assert len(response["workers"]) == dask.system.CPU_COUNT

    scheduler_addr = parse_address(response["scheduler"])
    scheduler_addr_protocol = scheduler_addr[0]
    scheduler_addr_host, _ = scheduler_addr[1].split(":")
    assert scheduler_addr_protocol == expected_protocol
    assert scheduler_addr_host == expected_host

    for _, worker_addr in response["workers"].items():
        protocol, host_and_port = parse_address(worker_addr)
        host, _ = host_and_port.split(":")
        assert protocol == expected_protocol
        assert host == expected_host


@pytest.mark.asyncio
async def test_cluster_restart(admin_worker_addr, event_loop):
    """
    Test restarting the cluster by asserting the addresses are different
    """
    asyncio.set_event_loop(event_loop)
    current_addresses = await _get_cluster_address(admin_worker_addr)

    # Restart the cluster
    await _cluster_restart(admin_worker_addr)

    new_addresses = await _get_cluster_address(admin_worker_addr)

    assert current_addresses != new_addresses


@pytest.mark.asyncio
async def test_cluster_scale_up_down(admin_worker_addr, event_loop):
    """
    Test scaling up/down by one worker
    """
    asyncio.set_event_loop(event_loop)

    target_cluster_size = dask.system.CPU_COUNT + 1
    try:
        await _cluster_scale(admin_worker_addr, target_cluster_size)

        # Having to wait here for the time it takes to create a new dask worker
        time.sleep(4)
        cluster_size = await _get_cluster_size(admin_worker_addr)
        assert cluster_size == target_cluster_size
    except TimeoutError:
        pass

    # Scale cluster back down
    try:
        await _cluster_scale(admin_worker_addr, dask.system.CPU_COUNT)
        time.sleep(4)
        cluster_size = await _get_cluster_size(admin_worker_addr)
        assert cluster_size == dask.system.CPU_COUNT
    except TimeoutError:
        pass
