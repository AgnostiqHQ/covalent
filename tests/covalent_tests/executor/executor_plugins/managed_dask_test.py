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

import os
import tempfile

import cloudpickle
import pytest

from covalent import TransportableObject


@pytest.mark.asyncio
async def test_managed_dask_send_poll_receive():
    """Test a full job execution sequence"""

    from dask.distributed import Future

    from covalent.executor.executor_plugins.managed_dask import ManagedDaskExecutor, _clients

    scheduler_address = os.environ.get("DASK_SCHEDULER_ADDR", None)
    if not scheduler_address:
        raise RuntimeError("DASK_SCHEDULER_ADDR not set")

    executor = ManagedDaskExecutor(scheduler_address, cache_dir="/tmp")

    def task(x, y):
        import sys

        print("HELLO!!")
        print("Error", file=sys.stderr)
        return x**3 + y

    serialized_fn = TransportableObject(task)
    serialized_x = TransportableObject(3)
    serialized_y = TransportableObject(1)

    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pkl") as temp:
        function_uri = temp.name
        cloudpickle.dump(serialized_fn, temp)

    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pkl") as temp:
        arg_uri = temp.name
        cloudpickle.dump(serialized_x, temp)

    with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pkl") as temp:
        kwarg_uri = temp.name
        cloudpickle.dump(serialized_y, temp)

    dispatch_id = "dispatch"
    node_id = 2
    task_metadata = {"dispatch_id": dispatch_id, "node_id": node_id}

    key = await executor.send(
        f"file://{function_uri}",
        "",
        "",
        "",
        [f"file://{arg_uri}"],
        {"y": kwarg_uri},
        task_metadata,
    )

    client = _clients[key]

    fut_2 = Future(key=key, client=client)
    await executor.poll(task_metadata, key)

    assert fut_2.done()

    output_uri, stdout_uri, stderr_uri, exception_raised = await executor.receive(
        task_metadata, key
    )

    with open(output_uri, "rb") as f:
        ser_output = cloudpickle.load(f)
        assert ser_output.get_deserialized() == 28

    with open(stdout_uri, "r") as f:
        assert f.read() == "HELLO!!\n"

    with open(stderr_uri, "r") as f:
        assert f.read() == "Error\n"

    os.unlink(function_uri)
    os.unlink(output_uri)
    os.unlink(stdout_uri)
    os.unlink(stderr_uri)
