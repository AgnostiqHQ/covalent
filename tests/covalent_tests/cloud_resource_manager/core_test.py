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

import os
import subprocess
import tempfile
from configparser import ConfigParser
from functools import partial
from pathlib import Path
from unittest import mock

import pytest

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
def executor_infra_defaults():
    from pydantic import BaseModel

    class FakeExecutorInfraDefaults(BaseModel):
        string_param: str = "fake_address_123"
        number_param: int = 123
        sequence_param: tuple = (1, 2, 3)

    return FakeExecutorInfraDefaults


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


class _FakeIO:
    """Mocks process stdout and stderr."""

    def __init__(self, message):
        self.message = message

    def read(self):
        return self.message

    def readline(self):
        return self.read()


class _FakeProc:
    """Mocks process"""

    def __init__(self, returncode, stdout="", stderr="", fake_stream=True):
        self.returncode = returncode
        self.args = ()
        self.stdout = _FakeIO(stdout) if fake_stream else stdout
        self.stderr = _FakeIO(stderr) if fake_stream else stderr

    def poll(self):
        return self.returncode

    def communicate(self):
        return self.stdout.read(), self.stderr.read()


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
    if not options:
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
            mock_validate_options.assert_called_once_with(
                mock_model_class, mock_model_class, options
            )
        else:
            mock_validate_options.assert_not_called()
    else:
        with pytest.raises(
            SystemExit,
        ):
            crm = CloudResourceManager(
                executor_name=executor_name,
                executor_module_path=executor_module_path,
                options=options,
            )


def test_poll_process(mocker, crm):
    """
    Unit test for CloudResourceManager._poll_process() method
    """

    test_stdout = "test_stdout".encode("utf-8")
    test_return_code = 0

    mock_process = mocker.MagicMock()

    mock_process.poll.side_effect = partial(next, iter([None, test_return_code, test_return_code]))
    mock_process.stdout.readline.side_effect = partial(next, iter([test_stdout, None]))

    mock_print = mocker.patch("covalent.cloud_resource_manager.core.print")
    return_code = crm._poll_process(
        mock_process,
        print_callback=mock_print(
            test_stdout.decode("utf-8"),
        ),
    )

    mock_process.stdout.readline.assert_called_once()
    mock_print.assert_called_once_with(test_stdout.decode("utf-8"))
    assert mock_process.poll.call_count == 2
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
    test_env_vars = {"test_env_key": "test_env_value"}

    mock_popen = mocker.patch(
        "covalent.cloud_resource_manager.core.subprocess.Popen",
        return_value=_FakeProc(test_retcode),
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._poll_process",
        return_value=int(test_retcode),
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.open",
    )
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._log_error_msg",
    )

    if test_retcode != 0:
        exception = subprocess.CalledProcessError(returncode=test_retcode, cmd=test_cmd)
        print("some exception ", exception)
        with pytest.raises(subprocess.CalledProcessError) as excinfo:
            crm._run_in_subprocess(
                cmd=test_cmd,
                env_vars=test_env_vars,
            )
            # Errors are contained in the output for printing.
            assert excinfo.value.output == "some exception "
    else:
        crm._run_in_subprocess(
            cmd=test_cmd,
            env_vars=test_env_vars,
        )

    mock_popen.assert_called_once_with(
        args=test_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=crm.executor_tf_path,
        universal_newlines=True,
        shell=True,
        env=test_env_vars,
    )


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
    crm.plugin_settings = mocker.MagicMock()
    crm.plugin_settings.return_value.dict.return_value = {test_key: test_value}
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
        mocker.patch(
            "covalent.cloud_resource_manager.core.subprocess.run",
            return_value=subprocess.CompletedProcess(
                args=["terraform --version"],
                returncode=0,
                stdout="Terraform v1.6.0\non linux_amd64\n\nYour version of Terraform is out of date! The latest version\nis 1.6.4. You can update by downloading from https://www.terraform.io/downloads.html\n",
                stderr="",
            ),
        )
        assert crm._get_tf_path() == test_tf_path
    else:
        with pytest.raises(
            SystemExit,
        ):
            crm._get_tf_path()

    mock_shutil_which.assert_called_once_with("terraform")


def test_get_tf_statefile_path(mocker, crm, executor_name):
    """
    Unit test for CloudResourceManager._get_tf_statefile_path() method
    """

    test_tf_state_file = "test_tf_state_file"

    # mock_get_config = mocker.patch(
    #     "covalent.cloud_resource_manager.core.get_config",
    #     return_value=test_tf_state_file,
    # )
    crm.executor_tf_path = test_tf_state_file

    assert crm._get_tf_statefile_path() == f"{test_tf_state_file}/terraform.tfstate"

    # mock_get_config.assert_called_once_with("dispatcher.db_path")


@pytest.mark.parametrize(
    "dry_run, executor_options",
    [
        (True, None),
        (False, {"test_key": "test_value"}),
    ],
)
def test_up(
    mocker, dry_run, executor_options, executor_name, executor_module_path, executor_infra_defaults
):
    """
    Unit test for CloudResourceManager.up() method
    """

    test_tf_path = "test_tf_path"
    test_tf_state_file = "test_tf_state_file"

    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_path",
        return_value=test_tf_path,
    )
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._validation_docker",
    )
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._get_tf_statefile_path",
        return_value=test_tf_state_file,
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.get_executor_module",
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

    if executor_options:
        with pytest.raises(SystemExit):
            CloudResourceManager(
                executor_name=executor_name,
                executor_module_path=executor_module_path,
                options=executor_options,
            )
    else:
        crm = CloudResourceManager(
            executor_name=executor_name,
            executor_module_path=executor_module_path,
            options=executor_options,
        )

        # Override infra defaults with dummy values.
        crm.ExecutorInfraDefaults = executor_infra_defaults

        with mock.patch(
            "covalent.cloud_resource_manager.core.open",
            mock.mock_open(),
        ) as mock_file:
            crm.up(dry_run=dry_run, print_callback=None)

        # mock_get_tf_path.assert_called_once()
        init_cmd = f"{test_tf_path} init"
        mock_run_in_subprocess.assert_any_call(
            cmd=init_cmd,
            env_vars=crm._terraform_log_env_vars,
            print_callback=None,
        )

        mock_environ_copy.assert_called_once()

        mock_run_in_subprocess.assert_any_call(
            cmd=f"{test_tf_path} plan -out tf.plan",  # -state={test_tf_state_file}",
            env_vars=crm._terraform_log_env_vars,
            print_callback=None,
        )

        if not dry_run:
            mock_run_in_subprocess.assert_any_call(
                cmd=f"{test_tf_path} apply tf.plan -state={test_tf_state_file}",
                env_vars=crm._terraform_log_env_vars,
                print_callback=None,
            )

            mock_update_config.assert_called_once_with(
                f"{crm.executor_tf_path}/{executor_name}.conf",
            )


def test_up_executor_options(mocker, executor_name, executor_module_path):
    """
    Unit test for CloudResourceManager.up() method with executor options.

    Test expected behavior with 'valid' options. Note that *actual* valid options
    require executor plugins to be installed, so not suitable for CI tests.
    """
    # Disable validation.
    mocker.patch(
        "covalent.cloud_resource_manager.core.validate_options",
        return_value=None,
    )
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._validation_docker",
    )

    # Disable actually finding executor.
    mocker.patch(
        "covalent.cloud_resource_manager.core.get_executor_module",
    )

    # Disable plugin settings.
    mocker.patch(
        "covalent.cloud_resource_manager.core.get_plugin_settings",
        return_value={},
    )

    # Disable path checks so nothing deleted (as it would be, if exists).
    mocker.patch("covalent.cloud_resource_manager.core.Path.exists", return_value=False)

    # Disable _run_in_subprocess to avoid side effects.
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._run_in_subprocess",
    )

    # Disable _update_config to avoid side effects.
    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._update_config",
    )

    # For CI tests, pretend homebrew exists.
    mocker.patch("shutil.which", return_value="/opt/homebrew/bin/terraform")
    mocker.patch(
        "covalent.cloud_resource_manager.core.subprocess.run",
        return_value=_FakeProc(0, stdout="v99.99", fake_stream=False),
    )

    crm = CloudResourceManager(
        executor_name=executor_name,
        executor_module_path=executor_module_path,
        options={"test_key": "test_value"},
    )

    with tempfile.TemporaryDirectory() as d:
        # Create fake vars file to avoid side effects.
        fake_tfvars_file = Path(d) / "terraform.tfvars"
        fake_tfvars_file.touch()

        crm.executor_tf_path = d
        crm.up(dry_run=False, print_callback=None)


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

    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._validation_docker",
    )

    log_file_path = os.path.join(crm.executor_tf_path + "/terraform-error.log")

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

    mocker.patch(
        "covalent.cloud_resource_manager.core.os.path.getsize",
        return_value=2,
    )

    crm.down(print_callback=None)

    mock_get_tf_path.assert_called_once()
    mock_get_tf_statefile_path.assert_called_once()
    cmd = " ".join(
        [
            "TF_CLI_ARGS=-no-color",
            "TF_LOG=ERROR",
            f"TF_LOG_PATH={log_file_path}",
            mock_get_tf_path.return_value,
            "destroy",
            "-auto-approve",
        ]
    )
    env_vars = crm._terraform_log_env_vars
    mock_run_in_subprocess.assert_called_once_with(cmd=cmd, print_callback=None, env_vars=env_vars)

    assert mock_path_exists.call_count == 5
    assert mock_path_unlink.call_count == 4


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

    mock_terraform_error_validator = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._terraform_error_validator",
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._validation_docker",
    )

    mocker.patch(
        "covalent.cloud_resource_manager.core.subprocess.Popen",
    )

    crm.status()

    mock_get_tf_path.assert_called_once()
    mock_get_tf_statefile_path.assert_called_once()
    mock_terraform_error_validator.assert_called_once_with(tfstate_path=test_tf_state_file)


def test_crm_get_resource_status(mocker, crm):
    """
    Unit test for CloudResourceManager._get_resource_status() method.

    Test that errors while getting resource status don't exit, rather print and report status.
    """

    mock_terraform_error_validator = mocker.patch(
        "covalent.cloud_resource_manager.core.CloudResourceManager._terraform_error_validator",
    )
    mock_print = mocker.patch(
        "covalent.cloud_resource_manager.core.print",
    )

    crm._get_resource_status(proc=_FakeProc(1), cmd="fake command")
    mock_print.assert_called_once()
    mock_terraform_error_validator.assert_called_once()


def test_crm_convert_to_tfvar(mocker, crm):
    """
    Unit test for CloudResourceManager._convert_to_tfvar() method.

    Test conversion outcomes.
    """
    _values_map = {
        # Convenient test case (not valid Terraform):
        (1, False, None, "covalent321"): '[1, false, null, "covalent321"]',
        # Usual test cases:
        True: "true",
        False: "false",
        None: "null",
        "covalent123": '"covalent123"',  # must include quotes
        16: "16",
    }

    for _value, _expected in _values_map.items():
        assert crm._convert_to_tfvar(_value) == _expected


def test_no_git(crm, mocker):
    """
    Test for exit with status 1 if `git` is not available.
    """

    mocker.patch("shutil.which", return_value=None)
    mocker.patch("covalent.cloud_resource_manager.CloudResourceManager._log_error_msg")

    with pytest.raises(SystemExit):
        crm._run_in_subprocess("fake command")


def test_tf_version_error(mocker, crm):
    """
    Unit test for CloudResourceManager._get_tf_path() method.
    """

    # Fail. Terraform not found on system.
    mocker.patch("shutil.which", return_value=None)
    with pytest.raises(SystemExit):
        crm._get_tf_path()

    fake_proc_1 = _FakeProc(0, stdout="v0.0", fake_stream=False)
    fake_proc_2 = _FakeProc(0, stdout="v99.99", fake_stream=False)

    # Fail. Old version of terraform found.
    mocker.patch("shutil.which", return_value="/opt/homebrew/bin/terraform")
    mocker.patch("subprocess.run", return_value=fake_proc_1)
    with pytest.raises(SystemExit):
        crm._get_tf_path()

    # Succeed.
    mocker.patch("subprocess.run", return_value=fake_proc_2)
    mocker.patch("covalent.cloud_resource_manager.core.logger.error")
    assert "terraform" in crm._get_tf_path()
