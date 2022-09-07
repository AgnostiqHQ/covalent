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

"""Tests for Covalent remote executor."""

import tempfile

import pytest

from covalent.executor.executor_plugins.remote_executor import RemoteExecutor


def _create_mock_executor():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = tempfile.NamedTemporaryFile(prefix="mock_credentials", suffix=".rsa", dir=tmpdir)
        executor = RemoteExecutor(poll_freq=10, remote_cache=tmpdir, credentials_file=tmpfile)

    return executor


def test_remote_executor_init():
    """Test remote executor constructor """

    mock_executor = _create_mock_executor()
    assert mock_executor.poll_freq == 10
    assert "mock_credentials" in mock_executor.credentials_file.name.split('/')[-1].split('.')[0]
    assert "rsa" in mock_executor.credentials_file.name.split('/')[-1].split('.')[-1]


@pytest.mark.asyncio
async def test_run_async_subprocess():
    """Test remote executor async subprocess call"""

    test_dir, test_file, non_existent_file = 'file_dir', 'file.txt', 'non_existent_file.txt'
    create_file = f"rm -rf {test_dir} && mkdir {test_dir} && cd {test_dir} && touch {test_file} && echo 'hello remote "\
                  f"executor' >> {test_file} "
    read_non_existent_file = f"cat {non_existent_file}"

    executor = _create_mock_executor()
    create_file_proc, create_file_stdout, create_file_stderr = await executor.run_async_subprocess(create_file)

    # Test that file creation works as expected
    assert create_file_proc == 0
    assert create_file_stdout == ''
    assert create_file_stderr == ''

    # Test that file was created and written to correctly
    try:
        with open(f'{test_dir}/{test_file}', 'r') as test_file:
            lines = test_file.readlines()
            assert lines[0].strip() == 'hello remote executor'

    except FileNotFoundError as fe:
        return str(fe)

    # Test that reading from a non-existent file throws an error and returns a non-zero exit code
    read_file_proc, read_file_stdout, read_file_stderr = await executor.run_async_subprocess(read_non_existent_file)

    assert read_file_proc == 1
    assert read_file_stderr.strip() == f'cat: {non_existent_file}: No such file or directory'


@pytest.mark.asyncio
async def test_validate_credentials():
    """Test validation of credentials"""
    res = await _create_mock_executor()._validate_credentials()
    assert res is None


@pytest.mark.asyncio
async def test_upload_task():
    """Test task upload"""
    res = await _create_mock_executor()._upload_task()
    assert res is None


@pytest.mark.asyncio
async def test_submit_task():
    """Test task submit"""
    res = await _create_mock_executor().submit_task()
    assert res is None


@pytest.mark.asyncio
async def test_get_status():
    """Test querying electron status"""
    res = await _create_mock_executor().get_status()
    assert res is None


@pytest.mark.asyncio
async def test_poll_task():
    """Test polling task execution status"""
    res = await _create_mock_executor()._poll_task()
    assert res is None


@pytest.mark.asyncio
async def test_query_result():
    """Test querying result from remote cache"""
    res = await _create_mock_executor().query_result()
    assert res is None


@pytest.mark.asyncio
async def test_cancel():
    """Test sending cancel workflow request to remote backend"""
    res = await _create_mock_executor().cancel()
    assert res is None
