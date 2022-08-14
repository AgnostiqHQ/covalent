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

"""Tests for the Covalent executor file monitor module."""

import os
import tempfile

import pytest

from covalent.executor.base import BaseAsyncExecutor
from covalent.executor.utils.filemonitor import AsyncFileMonitor


class MockAsyncExecutor(BaseAsyncExecutor):
    async def poll_file(self, path, starting_pos, size):
        try:
            with open(path, "r") as f:
                f.seek(starting_pos)
                contents = f.read(size)
        except:
            contents = ""
        return contents

    def get_files_to_monitor(self, dispatch_id, node_id):
        return []

    async def setup(self, task_metadata):
        pass

    async def run(self, function, args, kwargs, task_metadata):
        return function(*args, **kwargs)

    async def teardown(self, task_metadata):
        pass


@pytest.mark.asyncio
async def test_file_monitor_contents_generator():
    """Test file monitor"""
    me = MockAsyncExecutor()

    f = tempfile.NamedTemporaryFile("a", delete=False)
    tmp_path = f.name
    with f:
        f.write("Hello")

    filemon = AsyncFileMonitor(me, tmp_path, "/tmp/results", "asdf", 0)

    monitored_file = filemon.generate_file_contents(tmp_path)
    contents = await monitored_file.__anext__()
    assert contents == "Hello"
    with open(tmp_path, "a") as f:
        f.write("World")
    contents = await monitored_file.__anext__()
    assert contents == "World"

    with open(tmp_path, "r") as f:
        assert f.read() == "HelloWorld"

    os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_file_monitor_update_executor_info():
    """Test updating executor info log"""

    import json

    me = MockAsyncExecutor(log_info="info.log")
    tmp_path = "/var/log/profile.log"
    chunk = "Hello"
    dispatch_id = "asdf"
    results_dir = "/tmp"
    filemon = AsyncFileMonitor(me, tmp_path, results_dir, dispatch_id, 0)
    await filemon.update_executor_info(chunk)

    log_file_path = "/tmp/asdf/info.log"

    with open(log_file_path, "r") as f:
        contents = f.read()
    os.unlink(log_file_path)
    assert contents == "/var/log/profile.log: Hello"
