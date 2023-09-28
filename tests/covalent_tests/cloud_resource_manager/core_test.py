# Copyright 2023 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import subprocess
from configparser import ConfigParser
from functools import partial
from pathlib import Path
from unittest import mock

import pytest

from covalent._shared_files.exceptions import CommandNotFoundError
from covalent.cloud_resource_manager.core import (
    CloudResourceManager,
    get_executor_module,
    validate_options,
)


@pytest.fixture
def executor_name():
    return "test_executor"


@pytest.fixture
def executor_module_path():
    return "test_executor_module_path"


@pytest.fixture
def crm(mocker, executor_name, executor_module_path):
    mocker.patch(
        "covalent.cloud_resource_manager.core.get_executor_module",
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.getattr",
    )

    return CloudResourceManager(
        executor_name=executor_name,
        executor_module_path=executor_module_path,
    )


def test_get_executor_module(mocker):
    """
    Unit test for get_executor_module method
    """

    test_executor_name = "test_executor"
    test_executor_module = "test_executor_module"

    mock_import_module = mocker.patch(
        "covalent.cloud_resource_manager.core.importlib.import_module",
        return_value=test_executor_module,
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core._executor_manager.executor_plugins_map",
        return_value={test_executor_name: "test"},
    )

    returned_module = get_executor_module(test_executor_name)

    assert returned_module == test_executor_module
    mock_import_module.assert_called_once()


def test_validate_options(mocker):
    """
    Unit test for validate_options method
    """

    executor_options = {"test_key": "test_value"}

    mock_defaults_model = mocker.MagicMock()
    mocker.patch(
        "covalent.cloud_resource_manager.core.getattr",
        return_value=mock_defaults_model,
    )

    mock_list = mocker.patch(
        "covalent.cloud_resource_manager.core.list",
        return_value=list(executor_options.keys()),
    )

    validate_options(mock_defaults_model, mock_defaults_model, executor_options)

    assert mock_list.call_count == 2

    mock_defaults_model.assert_any_call(**executor_options)
    assert mock_defaults_model.call_count == 2


@pytest.mark.parametrize(
    "options",
    [
        None,
        {"test_key": "test_value"},
    ],
)
def test_cloud_resource_manager_init(mocker, options, executor_name, executor_module_path):
    """
    Unit test for CloudResourceManager's init method
    """

    mock_validate_options = mocker.patch(
        "covalent.cloud_resource_manager.core.validate_options",
    )

    mock_get_executor_module = mocker.patch(
        "covalent.cloud_resource_manager.core.get_executor_module",
    )

    mock_model_class = mocker.MagicMock()
    mocker.patch(
        "covalent.cloud_resource_manager.core.getattr",
        return_value=mock_model_class,
    )

    crm = CloudResourceManager(
        executor_name=executor_name,
        executor_module_path=executor_module_path,
        options=options,
    )

    assert crm.executor_name == executor_name
    assert crm.executor_tf_path == str(
        Path(executor_module_path).expanduser().resolve() / "assets" / "infra"
    )

    mock_get_executor_module.assert_called_once_with(executor_name)
    assert crm.executor_options == options

    if options:
        mock_validate_options.assert_called_once_with(mock_model_class, mock_model_class, options)
    else:
        mock_validate_options.assert_not_called()


def test_print_stdout(mocker, crm):
    """
    Unit test for CloudResourceManager._print_stdout() method
    """

    test_stdout = "test_stdout".encode("utf-8")
    test_return_code = 0

    mock_process = mocker.MagicMock()

    mock_process.poll.side_effect = partial(next, iter([None, test_return_code, test_return_code]))
    mock_process.stdout.readline.side_effect = partial(next, iter([test_stdout, None]))

    mock_print = mocker.patch("covalent.cloud_resource_manager.core.print")

    return_code = crm._print_stdout(mock_process)

    mock_process.stdout.readline.assert_called_once()
    mock_print.assert_called_once_with(test_stdout.decode("utf-8"))
    assert mock_process.poll.call_count == 3
    assert return_code == test_return_code


@pytest.mark.parametrize(
    "test_retcode",
    [
        0,
        1,
    ],
)
def test_run_in_subprocess(mocker, test_retcode, crm):
    """
    Unit test for CloudResourceManager._run_in_subprocess() method.
    """

    test_cmd = "test_cmd"
    test_workdir = "test_workdir"
    test_env_vars = {"test_env_key": "test_env_value"}

    mock_process = mocker.MagicMock()
    mock_popen = mocker.patch(
        "covalent.cloud_resource_manager.core.subprocess.Popen",
        return_value=mock_process,
    )

    mock_print_stdout = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._print_stdout",
        return_value=test_retcode,
    )

    if test_retcode != 0:
        exception = subprocess.CalledProcessError(returncode=test_retcode, cmd=test_cmd)
        with pytest.raises(Exception, match=str(exception)):
            crm._run_in_subprocess(
                cmd=test_cmd,
                workdir=test_workdir,
                env_vars=test_env_vars,
            )
    else:
        crm._run_in_subprocess(
            cmd=test_cmd,
            workdir=test_workdir,
            env_vars=test_env_vars,
        )

    mock_popen.assert_called_once_with(
        args=test_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=test_workdir,
        shell=True,
        env=test_env_vars,
    )

    mock_print_stdout.assert_called_once_with(mock_process)


def test_update_config(mocker, crm, executor_name):
    """
    Unit test for CloudResourceManager._update_config() method.
    """

    test_tf_executor_config_file = "test_tf_executor_config_file"
    test_key = "test_key"
    test_value = "test_value"

    test_config_parser = ConfigParser()
    test_config_parser[executor_name] = {test_key: test_value}
    test_config_parser.read = mocker.MagicMock()

    crm.ExecutorPluginDefaults = mocker.MagicMock()
    crm.ExecutorPluginDefaults.return_value.dict.return_value = {test_key: test_value}

    mocker.patch(
        "covalent.cloud_resource_manager.core.ConfigParser",
        return_value=test_config_parser,
    )

    mock_set_config = mocker.patch(
        "covalent.cloud_resource_manager.core.set_config",
    )

    crm._update_config(
        tf_executor_config_file=test_tf_executor_config_file,
    )

    test_config_parser.read.assert_called_once_with(test_tf_executor_config_file)
    mock_set_config.assert_called_once_with(
        {f"executors.{executor_name}.{test_key}": test_value},
    )


@pytest.mark.parametrize(
    "test_tf_path",
    [
        "test_tf_path",
        None,
    ],
)
def test_get_tf_path(mocker, test_tf_path, crm):
    """
    Unit test for CloudResourceManager._get_tf_path() method
    """

    mock_shutil_which = mocker.patch(
        "covalent.cloud_resource_manager.core.shutil.which",
        return_value=test_tf_path,
    )

    if test_tf_path:
        assert crm._get_tf_path() == test_tf_path
    else:
        with pytest.raises(CommandNotFoundError, match="Terraform not found on system"):
            crm._get_tf_path()

    mock_shutil_which.assert_called_once_with("terraform")


def test_get_tf_statefile_path(mocker, crm, executor_name):
    """
    Unit test for CloudResourceManager._get_tf_statefile_path() method
    """

    test_tf_state_file = "test_tf_state_file"

    mock_get_config = mocker.patch(
        "covalent.cloud_resource_manager.core.get_config",
        return_value=test_tf_state_file,
    )

    assert crm._get_tf_statefile_path() == f"{executor_name}.tfstate"

    mock_get_config.assert_called_once_with("dispatcher.db_path")


@pytest.mark.parametrize(
    "dry_run, executor_options",
    [
        (True, None),
        (False, {"test_key": "test_value"}),
    ],
)
def test_up(mocker, dry_run, executor_options, executor_name, executor_module_path):
    """
    Unit test for CloudResourceManager.up() method
    """

    test_tf_path = "test_tf_path"
    test_tf_state_file = "test_tf_state_file"

    mock_get_tf_path = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_path",
        return_value=test_tf_path,
    )

    mock_get_tf_statefile_path = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_statefile_path",
        return_value=test_tf_state_file,
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.get_executor_module",
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.getattr",
    )

    # Mocking as we are instantiating with executor options
    mocker.patch(
        "covalent.cloud_resource_manager.core.validate_options",
    )

    mock_run_in_subprocess = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._run_in_subprocess",
    )

    test_tf_dict = {"test_tf_key": "test_tf_value"}
    mock_environ_copy = mocker.patch(
        "covalent.cloud_resource_manager.core.os.environ.copy",
        return_value=test_tf_dict,
    )

    mock_update_config = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._update_config",
    )

    crm = CloudResourceManager(
        executor_name=executor_name,
        executor_module_path=executor_module_path,
        options=executor_options,
    )

    with mock.patch(
        "covalent.cloud_resource_manager.core.open",
        mock.mock_open(),
    ) as mock_file:
        crm.up(dry_run=dry_run)

    mock_get_tf_path.assert_called_once()
    mock_get_tf_statefile_path.assert_called_once()
    mock_run_in_subprocess.assert_any_call(
        cmd=f"{test_tf_path} init",
        workdir=crm.executor_tf_path,
    )

    mock_environ_copy.assert_called_once()

    if executor_options:
        mock_file.assert_called_once_with(
            f"{crm.executor_tf_path}/terraform.tfvars",
            "w",
        )

        key, value = list(executor_options.items())[0]
        mock_file().write.assert_called_once_with(f'{key}="{value}"\n')

    mock_run_in_subprocess.assert_any_call(
        cmd=f"{test_tf_path} plan -out tf.plan -state={test_tf_state_file}",
        workdir=crm.executor_tf_path,
        env_vars=test_tf_dict,
    )

    if not dry_run:
        mock_run_in_subprocess.assert_any_call(
            cmd=f"{test_tf_path} apply tf.plan -state={test_tf_state_file}",
            workdir=crm.executor_tf_path,
            env_vars=test_tf_dict,
        )

        mock_update_config.assert_called_once_with(
            f"{crm.executor_tf_path}/{executor_name}.conf",
        )


def test_down(mocker, crm):
    """
    Unit test for CloudResourceManager.down() method.
    """

    test_tf_path = "test_tf_path"
    test_tf_state_file = "test_tf_state_file"

    mock_get_tf_path = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_path",
        return_value=test_tf_path,
    )

    mock_get_tf_statefile_path = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_statefile_path",
        return_value=test_tf_state_file,
    )

    mock_run_in_subprocess = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._run_in_subprocess",
    )

    mock_path_exists = mocker.patch(
        "covalent.cloud_resource_manager.core.Path.exists",
        return_value=True,
    )

    mock_path_unlink = mocker.patch(
        "covalent.cloud_resource_manager.core.Path.unlink",
    )

    crm.down()

    mock_get_tf_path.assert_called_once()
    mock_get_tf_statefile_path.assert_called_once()
    mock_run_in_subprocess.assert_called_once_with(
        cmd=f"{mock_get_tf_path.return_value} destroy -auto-approve -state={test_tf_state_file}",
        workdir=crm.executor_tf_path,
    )

    assert mock_path_exists.call_count == 2
    assert mock_path_unlink.call_count == 3


def test_status(mocker, crm):
    """
    Unit test for CloudResourceManager.status() method.
    """

    test_tf_path = "test_tf_path"
    test_tf_state_file = "test_tf_state_file"

    mock_get_tf_path = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_path",
        return_value=test_tf_path,
    )

    mock_get_tf_statefile_path = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_statefile_path",
        return_value=test_tf_state_file,
    )

    mock_run_in_subprocess = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._run_in_subprocess",
    )

    crm.status()

    mock_get_tf_path.assert_called_once()
    mock_get_tf_statefile_path.assert_called_once()
    mock_run_in_subprocess.assert_called_once_with(
        cmd=f"{test_tf_path} state list -state={test_tf_state_file}",
        workdir=crm.executor_tf_path,
    )
