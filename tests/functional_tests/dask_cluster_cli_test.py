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

import ast
import time

import dask.system
import pytest
from click.testing import CliRunner
from distributed.comm import parse_address

from covalent._shared_files.config import get_config
from covalent_dispatcher._cli.service import _is_server_running, cluster


@pytest.fixture(autouse=True)
def covalent():
    """
    Check to see if covalent is already running in the default
    configuration
    """
    assert _is_server_running()


def test_worker_config_option():
    """
    Assert that `num_workers` exists as a key in covalent.conf/dask
    """
    num_workers = get_config("dask.num_workers")
    assert int(num_workers) == dask.system.CPU_COUNT


@pytest.mark.skip(reason="unstable test")
def test_cluster_size_cli():
    """
    Assert covalent cluster size is equal to the default value
    """
    runner = CliRunner()
    response = runner.invoke(cluster, "--size")
    assert int(response.output) == dask.system.CPU_COUNT


@pytest.mark.skip(reason="unstable test")
def test_cluster_status_cli():
    """
    Assert cluster status CLI for default number of workers in the cluster
    """
    runner = CliRunner()
    response = runner.invoke(cluster, "--status")
    expected = {}
    expected["scheduler"] = "running"
    for i in range(dask.system.CPU_COUNT):
        expected[f"worker-{i}"] = "running"

    assert expected == ast.literal_eval(response.output)


@pytest.mark.skip(reason="unstable test")
def test_cluster_info_cli():
    """
    Test cluster info CLI for default number of workers, memory and threads per
    worker
    """
    runner = CliRunner()
    response = ast.literal_eval(runner.invoke(cluster, "--info").output)
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
    assert list(response.keys()) == expected_keys
    assert len(response["workers"]) == dask.system.CPU_COUNT

    # Check the keys match for each worker in the cluster
    for _, value in response["workers"].items():
        assert list(value.keys()) == worker_info_expected_keys


@pytest.mark.skip(reason="unstable test")
def test_cluster_address_cli():
    """
    Test cluster address CLI
    """
    runner = CliRunner()
    expected_protocol = "tcp"
    expected_host = "127.0.0.1"

    response = ast.literal_eval(runner.invoke(cluster, "--address").output)
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


@pytest.mark.skip(reason="unstable test")
def test_cluster_restart():
    """
    Test restarting the cluster by asserting the addresses are different
    """
    runner = CliRunner()
    current_addresses = ast.literal_eval(runner.invoke(cluster, "--address").output)

    response = runner.invoke(cluster, "--restart").output
    assert response == "Cluster restarted\n"

    new_addresses = ast.literal_eval(runner.invoke(cluster, "--address").output)

    assert current_addresses != new_addresses


@pytest.mark.skip(reason="unstable test")
def test_cluster_scale_up_down():
    """
    Test scaling up/down by one worker
    """
    target_cluster_size = dask.system.CPU_COUNT + 1
    runner = CliRunner()
    try:
        response = runner.invoke(cluster, f"--scale {target_cluster_size}")
        assert response.output == f"Cluster scaled to have {target_cluster_size} workers\n"
        # Having to wait here for the time it takes to create a new dask worker
        time.sleep(4)
        response = runner.invoke(cluster, "--size")
        assert int(response.output) == target_cluster_size
    except TimeoutError:
        pass

    # Scale cluster back down
    try:
        response = runner.invoke(cluster, f"--scale {dask.system.CPU_COUNT}")
        assert response.output == f"Cluster scaled to have {dask.system.CPU_COUNT} workers\n"
        time.sleep(4)
        response = runner.invoke(cluster, "--size")
        assert int(response.output) == dask.system.CPU_COUNT
    except TimeoutError:
        pass
