import pytest
import ast
import os
import subprocess
import asyncio
from subprocess import PIPE
from covalent_dispatcher._service.app_dask import DaskCluster
from covalent_dispatcher._cli.service import cluster_status, _is_server_running
from covalent._shared_files.config import get_config
from covalent._shared_files import logger
from click.testing import CliRunner
from covalent_dispatcher._cli.service import (
    cluster,
    cluster_status,
    cluster_info,
    cluster_address,
    cluster_worker_count,
    cluster_logs
)
from distributed.core import rpc


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def covalent():
    """
    Yield the required connection TCP connection strings for the
    tests to run, assuming covalent is already running
    """
    assert _is_server_running()

    runner = CliRunner()
    scheduler_address = get_config("dask.scheduler_address")
    admin_host = get_config("dask.admin_host")
    admin_port = get_config("dask.admin_port")
    return {"cli_runner": runner, "scheduler_address": scheduler_address, "admin_host": admin_host,
            "admin_port": admin_port}


def test_cluster_status(covalent, event_loop):
    """
    Test that the status cli returns the status of the scheduler and
    all cluster workers
    """
    # Invoke the cluster_status method directly
    expected = event_loop.run_until_complete(cluster_status(covalent["scheduler_address"]))

    cli_response = covalent["cli_runner"].invoke(cluster, ["--status"])

    assert expected == ast.literal_eval(cli_response.output)


def test_cluster_info(covalent, event_loop):
    """
    Test that cluster info CLI works
    """
    expected = event_loop.run_until_complete(cluster_info(covalent["scheduler_address"]))

    # Invoke the CLI
    cli_response = covalent["cli_runner"].invoke(cluster, ["--info"])

    assert expected == ast.literal_eval(cli_response.output)


def test_cluster_address(covalent, event_loop):
    expected = event_loop.run_until_complete(cluster_address(covalent["scheduler_address"]))

    # Invoke cluster --address CLI
    cli_response = covalent["cli_runner"].invoke(cluster, ["--address"])

    assert expected == ast.literal_eval(cli_response.output)


def test_cluster_nworkers(covalent, event_loop):
    # Get current cluster worker count
    current_worker_count = event_loop.run_until_complete(cluster_worker_count(covalent["scheduler_address"]))

    # Invoke covalent cluster --nworkers
    cli_response = covalent["cli_runner"].invoke(cluster, ["--nworkers"])
    assert current_worker_count == int(cli_response.output)


def test_cluster_restart(covalent, event_loop):
    # Get current cluster addresses i.e (scheduler and workers)
    current_addresses = event_loop.run_until_complete(cluster_address(covalent["scheduler_address"]))

    # Now restart the cluster using covalent cluster --restart
    cli_response = covalent["cli_runner"].invoke(cluster, ["--restart"])

    # Get new addresses
    new_addresses = event_loop.run_until_complete(cluster_address(covalent["scheduler_address"]))

    # Assert new addresses are different from current ones
    assert current_addresses != new_addresses


@pytest.mark.skip(reason="Pending implementation")
def test_cluster_scale_up(covalent, event_loop):
    # To be implemented
    pass


@pytest.mark.skip(reason="Pending implementation")
def test_cluster_scale_down(covalent, event_loop):
    # to be implemented
    pass
