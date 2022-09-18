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

"""Tests for Covalent dask executor."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest


def test_dask_executor_init(mocker):
    """Test dask executor constructor"""

    from covalent.executor import DaskExecutor

    de = DaskExecutor("127.0.0.1")

    assert de.scheduler_address == "127.0.0.1"
    assert de.time_limit == -1
    assert de.retries == 0


def test_dask_wrapper_fn():
    import sys

    from covalent.executor.executor_plugins.dask import dask_wrapper

    def f(x):
        print("Hello", file=sys.stdout)
        print("Bye", file=sys.stderr)
        return x

    args = [5]
    kwargs = {}
    output, stdout, stderr = dask_wrapper(f, args, kwargs)
    assert output == 5
    assert stdout == "Hello\n"
    assert stderr == "Bye\n"


def test_dask_executor_run():
    """Test run method for Dask executor"""
    import io
    import sys
    from contextlib import redirect_stderr, redirect_stdout

    from dask.distributed import LocalCluster

    from covalent.executor import DaskExecutor

    cluster = LocalCluster()

    dask_exec = DaskExecutor(cluster.scheduler_address)

    def f(x, y):
        print("Hello", file=sys.stdout)
        print("Bye", file=sys.stderr)
        return x, y

    args = [5]
    kwargs = {"y": 7}
    task_metadata = {"dispatch_id": "asdf", "node_id": 1}
    dask_exec._initialize_runtime()
    dask_exec._initialize_task_data("asdf", 1)

    with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
        result = asyncio.run(dask_exec.run(f, args, kwargs, task_metadata))

    assert result == (5, 7)
    assert stdout.getvalue() == "Hello\n"
    assert stderr.getvalue() == "Bye\n"


@pytest.mark.asyncio
async def test_dask_executor_cancel(mocker):
    """Test cancel method for Dask executor"""

    from covalent.executor import DaskExecutor

    dask_exec = DaskExecutor("localhost:5873")
    key = "a"
    mock_cancel_fut = AsyncMock()
    dispatch_id = "test_dispatch"
    node_id = 1
    fut = MagicMock()
    fut.cancel = mock_cancel_fut
    get_data_mock = mocker.patch(
        "covalent.executor.base.AsyncBaseExecutor._get_task_data", return_value=fut
    )

    await dask_exec.cancel(dispatch_id, node_id)

    get_data_mock.assert_called_once_with(dispatch_id, node_id, "dask_future")

    mock_cancel_fut.assert_awaited_once()
