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

"""Tests for the Covalent executor base module."""

import os
import tempfile

import covalent as ct
from covalent._workflow.transport import TransportableObject
from covalent.executor import BaseExecutor, wrapper_fn


class MockExecutor(BaseExecutor):
    def execute(self):
        pass


def test_write_streams_to_file(mocker):
    """Test write log streams to file method in BaseExecutor via LocalExecutor."""

    me = MockExecutor()

    # Case 1 - Check that relative log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = "relative.log"
        me.write_streams_to_file(
            stream_strings=["relative"], filepaths=[tmp_file], dispatch_id="", results_dir=tmp_dir
        )
        assert "relative.log" in os.listdir(tmp_dir)

        with open(f"{tmp_dir}/relative.log") as f:
            lines = f.readlines()
        assert lines[0] == "relative"

    # Case 2 - Check that absolute log files that are written to are constructed in the results directory that is explicitly passed as an argument.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = tempfile.NamedTemporaryFile()
        me.write_streams_to_file(
            stream_strings=["absolute"],
            filepaths=[tmp_file.name],
            dispatch_id="",
            results_dir=tmp_dir,
        )
        assert os.path.isfile(tmp_file.name)

        with open(tmp_file.name) as f:
            lines = f.readlines()
        assert lines[0] == "absolute"


def test_execute_in_conda_env(mocker):
    """Test execute in conda enve method in Base Executor object."""

    me = MockExecutor()

    mocker.patch("covalent.executor.BaseExecutor.get_conda_path", return_value=False)
    conda_env_fail_mock = mocker.patch("covalent.executor.BaseExecutor._on_conda_env_fail")
    me.execute_in_conda_env(
        "function",
        "function_version",
        "args",
        "kwargs",
        "conda_env",
        "cache_dir",
        "node_id",
    )
    conda_env_fail_mock.assert_called_once_with("function", "args", "kwargs", "node_id")


def test_wrapper_fn_calldep_retval_injection():
    """Test injecting calldep return values into main task"""

    def f(x=0, y=0):
        return x + y

    def identity(y):
        return y

    serialized_fn = TransportableObject(f)
    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")
    call_before = [calldep.apply()]
    args = []
    kwargs = {"x": 2}

    output = wrapper_fn(serialized_fn, call_before, [], *args, **kwargs)

    assert output == 7
