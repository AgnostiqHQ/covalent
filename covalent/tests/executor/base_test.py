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
import shutil
import tempfile
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import call

import cloudpickle as pickle
import pytest

from covalent.executor import BaseExecutor


class MockExecutor(BaseExecutor):
    def execute(self):
        pass


class SubprocMock:
    def __init__(self):
        self.stdout = ""
        self.stderr = ""


@pytest.mark.skip(reason="Needs to be refactored")
def test_base_init(mocker):
    mocker.patch.multiple(BaseExecutor, __abstractmethods__=set())

    executor = BaseExecutor(
        log_stdout="logout",
        log_stderr="logerr",
        conda_env="conda",
        cache_dir="cache",
        current_env_on_conda_fail=True,
    )

    assert executor.log_stdout == "logout"
    assert executor.log_stderr == "logerr"
    assert executor.conda_env == "conda"
    assert executor.cache_dir == "cache"
    assert executor.current_env_on_conda_fail
    assert executor.current_env == ""


@pytest.mark.skip(reason="Needs to be refactored")
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


@pytest.mark.skip(reason="Needs to be refactored")
@pytest.mark.parametrize(
    "conda_installed,successful_task,index", [(True, True, 0), (True, False, 1), (False, False, 2)]
)
def test_execute_in_conda_env(mocker, conda_installed, successful_task, index):
    """Test execute in conda enve method in Base Executor object."""

    with tempfile.TemporaryDirectory() as tmp_cache:
        me = MockExecutor(cache_dir=tmp_cache)
        me.conda_path = "/path/to/conda"

        subproc = SubprocMock()
        subproc.stdout = ""
        subproc.stderr = "Error"
        subproc.returncode = 0 if successful_task else 1

        def test_func(a, /, *, b):
            return a + b

        result_filename = f"{tmp_cache}/result_pickle_file{index}.pkl"
        with open(result_filename, "wb") as f:
            pickle.dump(3, f)

        def get_temp_file(dir, delete=None, mode=None):
            if delete is not None:
                return open(f"pickle_file{index}.pkl", "wb")
            elif mode == "w":
                return open(f"script_file{index}.sh", "w")

        get_conda_path_mock = mocker.patch(
            "covalent.executor.BaseExecutor.get_conda_path", return_value=conda_installed
        )
        conda_env_fail_mock = mocker.patch(
            "covalent.executor.base.BaseExecutor._on_conda_env_fail"
        )
        pickle_dump_mock = mocker.patch("covalent.executor.base.pickle.dump", return_value=None)
        pickle_load_mock = mocker.patch("covalent.executor.base.pickle.load", return_value=3)
        tempfile_mock = mocker.patch("tempfile.NamedTemporaryFile", side_effect=get_temp_file)
        path_exists_mock = mocker.patch("os.path.exists", return_value=conda_installed)
        subprocess_mock = mocker.patch("subprocess.run", return_value=subproc)

        result = me.execute_in_conda_env(
            fn=test_func,
            fn_version="function_version",
            args=[1],
            kwargs={"b": 2},
            conda_env="conda_env",
            cache_dir=tmp_cache,
            node_id=100,
        )

        get_conda_path_mock.assert_called_once_with()
        if (not conda_installed) or (not successful_task):
            conda_env_fail_mock.assert_called_once_with(test_func, [1], {"b": 2}, 100)
            if conda_installed:
                os.remove(f"pickle_file{index}.pkl")
                os.remove(f"script_file{index}.sh")
            return

        assert Path(f"pickle_file{index}.pkl").exists()
        assert Path(f"script_file{index}.sh").exists()

        tempfile_mock.assert_has_calls(
            [call(dir=tmp_cache, delete=False), call(dir=tmp_cache, mode="w")]
        )
        pickle_dump_mock.assert_called_once()
        path_exists_mock.assert_called_once_with("/path/to/../etc/profile.d/conda.sh")
        subprocess_mock.assert_called_once_with(
            ["bash", f"script_file{index}.sh"], capture_output=True, encoding="utf-8"
        )
        pickle_load_mock.assert_called_once()

        os.remove(f"pickle_file{index}.pkl")
        os.remove(f"script_file{index}.sh")


@pytest.mark.skip(reason="Needs to be refactored")
@pytest.mark.parametrize("use_current", [True, False])
def test_conda_env_fail(mocker, use_current):
    me = MockExecutor()
    me.conda_path = "/path/to/conda"
    me.current_env_on_conda_fail = use_current

    def test_func(a, /, *, b):
        return a + b

    node_id = 1

    context = pytest.raises(RuntimeError) if not use_current else nullcontext()

    with context:
        result = me._on_conda_env_fail(test_func, [1], {"b": 2}, node_id)

    if use_current:
        assert result == 3


@pytest.mark.skip(reason="Needs to be refactored")
def test_get_conda_envs(mocker):
    conda_env_str = """\
# conda environments:
#
base * /home/user/miniconda3
test /home/user/miniconda3/envs/test\
"""

    subproc = SubprocMock()
    subproc.stdout = conda_env_str
    subprocess_mocker = mocker.patch("subprocess.run", return_value=subproc)

    me = MockExecutor()
    me.get_conda_envs()

    subprocess_mocker.assert_called_once_with(
        ["conda", "env", "list"], capture_output=True, encoding="utf-8"
    )
    assert me.conda_envs == ["base", "test"]
    assert me.current_env == "base"
