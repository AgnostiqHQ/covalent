# Copyright 2023 Agnostiq Inc.
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


import importlib
import os
import shutil
import subprocess
from configparser import ConfigParser
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional

from covalent._shared_files.config import get_config, set_config
from covalent._shared_files.exceptions import CommandNotFoundError
from covalent.executor import _executor_manager


def get_executor_module(executor_name: str) -> ModuleType:
    """
    Get the executor module from the executor name

    Args:
        executor_name: Name of the executor

    Returns:
        The executor module

    """
    return importlib.import_module(
        _executor_manager.executor_plugins_map[executor_name].__module__
    )


def validate_options(
    ExecutorPluginDefaults, ExecutorInfraDefaults, executor_options: Dict[str, str]
) -> None:
    """
    Validate the options passed to the CRM

    Args:
        ExecutorPluginDefaults: Executor plugin defaults validation class
        ExecutorInfraDefaults: Executor infra defaults validation class
        executor_options: Options passed to the CRM

    Raises:
        pydantic.ValidationError: If the options are invalid

    """
    # Validating the passed options:

    plugin_attrs = list(ExecutorPluginDefaults.schema()["properties"].keys())
    infra_attrs = list(ExecutorInfraDefaults.schema()["properties"].keys())

    plugin_params = {k: v for k, v in executor_options.items() if k in plugin_attrs}
    infra_params = {k: v for k, v in executor_options.items() if k in infra_attrs}

    # Validate options
    ExecutorPluginDefaults(**plugin_params)
    ExecutorInfraDefaults(**infra_params)


def get_plugin_settings(
    ExecutorPluginDefaults, ExecutorInfraDefaults, executor_options: Dict
) -> Dict:
    """Get plugin settings.

    Args:
        ExecutorPluginDefaults: Executor plugin defaults validation class.
        ExecutorInfraDefaults: Executor infra defaults validation class.
        executor_options: Resource provisioning options passed to the CRM.

    Returns:
        Dictionary of plugin settings.

    """
    plugin_settings = ExecutorPluginDefaults.schema()["properties"]
    infra_settings = ExecutorInfraDefaults.schema()["properties"]

    settings_dict = {
        key: {
            "required": "No",
            "default": value["default"],
            "value": value["default"],
        }
        if "default" in value
        else {"required": "Yes", "default": None, "value": None}
        for key, value in plugin_settings.items()
    }
    for key, value in infra_settings.items():
        if "default" in value:
            settings_dict[key] = {
                "required": "No",
                "default": value["default"],
                "value": value["default"],
            }
        else:
            settings_dict[key] = {"required": "Yes", "default": None, "value": None}

    if executor_options:
        for key, value in executor_options.items():
            settings_dict[key]["value"] = value

    return settings_dict


class CloudResourceManager:
    """
    Base cloud resource manager class
    """

    def __init__(
        self,
        executor_name: str,
        executor_module_path: str,
        options: Optional[Dict[str, str]] = None,
    ):
        self.executor_name = executor_name
        self.executor_tf_path = str(
            Path(executor_module_path).expanduser().resolve() / "assets" / "infra"
        )

        # Includes both plugin and infra options
        self.executor_options = options

        # Importing validation classes from the executor module
        module = get_executor_module(executor_name)
        self.ExecutorPluginDefaults = getattr(module, "ExecutorPluginDefaults")
        self.ExecutorInfraDefaults = getattr(module, "ExecutorInfraDefaults")

        if self.executor_options:
            validate_options(
                self.ExecutorPluginDefaults, self.ExecutorInfraDefaults, self.executor_options
            )

        self.plugin_settings = get_plugin_settings(
            self.ExecutorPluginDefaults, self.ExecutorInfraDefaults, self.executor_options
        )

        self._terraform_log_env_vars = {
            "TF_LOG": "ERROR",
            "TF_LOG_PATH": Path(self.executor_tf_path) / "terraform-error.log",
        }

    def _print_stdout(self, process: subprocess.Popen, print_callback: Callable) -> int:
        """
        Print the stdout from the subprocess to console

        Args:
            process: Python subprocess whose stdout is to be printed to screen.
            print_callback: Callback function to print the stdout.

        Returns:
            Return code of the process.

        """
        while (retcode := process.poll()) is None:
            if (proc_stdout := process.stdout.readline()) and print_callback:
                print_callback(proc_stdout.strip().decode("utf-8"))
        return retcode

        # TODO: Return the command output along with return code

    def _parse_terraform_error_log(self) -> List[str]:
        """Parse the terraform error logs.

        Returns:
            List of lines in the terraform error log.

        """
        with open(self._terraform_log_env_vars["TF_LOG_PATH"], "r") as f:
            lines = f.readlines()
        return lines

    def _run_in_subprocess(
        self,
        cmd: str,
        workdir: str,
        env_vars: Optional[Dict[str, str]] = None,
        print_callback: Optional[Callable] = None,
    ) -> None:
        """
        Run the `cmd` in a subprocess shell with the env_vars set in the process's new environment

        Args:
            cmd: Command to execute in the subprocess
            workdir: Working directory of the subprocess
            env_vars: Dictionary of environment variables to set in the processes execution environment

        Returns:
            None

        """
        proc = subprocess.Popen(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=workdir,
            shell=True,
            env=env_vars,
        )
        retcode = self._print_stdout(proc, print_callback)

        if retcode != 0:
            raise subprocess.CalledProcessError(
                returncode=retcode, cmd=cmd, stderr=self._parse_terraform_error_log()
            )

    def _update_config(self, tf_executor_config_file: str) -> None:
        """
        Update covalent configuration with the executor
        config values as obtained from terraform

        Args:
            tf_executor_config_file: Path to the terraform executor config file

        Returns:
            None

        """
        # Puts the plugin options in covalent's config
        executor_config = ConfigParser()
        executor_config.read(tf_executor_config_file)

        filtered_executor_config = {
            k: v if v != "null" else None for k, v in executor_config[self.executor_name].items()
        }

        validated_config = self.ExecutorPluginDefaults(**filtered_executor_config).dict()

        for key, value in validated_config.items():
            set_config({f"executors.{self.executor_name}.{key}": value})
            self.plugin_settings[key]["value"] = value

    def _get_tf_path(self) -> str:
        """
        Get the terraform path

        Args:
            None

        Returns:
            Path to terraform executable

        """
        if terraform := shutil.which("terraform"):
            return terraform
        else:
            raise CommandNotFoundError("Terraform not found on system")

    def _get_tf_statefile_path(self) -> str:
        """
        Get the terraform state file path

        Args:
            None

        Returns:
            Path to terraform state file

        """
        # Saving in a directory which doesn't get deleted on purge
        return str(Path(get_config("dispatcher.db_path")).parent / f"{self.executor_name}.tfstate")

    def up(self, print_callback: Callable, dry_run: bool = True):
        """
        Spin up executor resources with terraform

        Args:
            dry_run: If True, only run terraform plan and not apply

        Returns:
            None

        """
        terraform = self._get_tf_path()

        tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"
        tf_executor_config_file = Path(self.executor_tf_path) / f"{self.executor_name}.conf"

        tf_init = " ".join(["TF_CLI_ARGS=-no-color", terraform, "init"])
        tf_plan = " ".join(["TF_CLI_ARGS=-no-color", terraform, "plan", "-out", "tf.plan"])
        tf_apply = " ".join(["TF_CLI_ARGS=-no-color", terraform, "apply", "tf.plan"])

        # Run `terraform init`
        self._run_in_subprocess(
            cmd=tf_init, workdir=self.executor_tf_path, env_vars=self._terraform_log_env_vars
        )

        # Setup terraform infra variables as passed by the user
        tf_vars_env_dict = os.environ.copy()

        if self.executor_options:
            with open(tfvars_file, "w") as f:
                for key, value in self.executor_options.items():
                    tf_vars_env_dict[f"TF_VAR_{key}"] = value

                    # Write whatever the user has passed to the terraform.tfvars file
                    f.write(f'{key}="{value}"\n')

        # Run `terraform plan`
        self._run_in_subprocess(
            cmd=tf_plan,
            workdir=self.executor_tf_path,
            env_vars=tf_vars_env_dict.update(self._terraform_log_env_vars),
            print_callback=print_callback,
        )

        # terraform_log_file = self._terraform_log_env_vars["TF_LOG_PATH"]
        # if Path(terraform_log_file).exists():
        #     Path(terraform_log_file).unlink()

        # Create infrastructure as per the plan
        # Run `terraform apply`
        if not dry_run:
            cmd_output = self._run_in_subprocess(
                cmd=tf_apply,
                workdir=self.executor_tf_path,
                env_vars=tf_vars_env_dict.update(self._terraform_log_env_vars),
                print_callback=print_callback,
            )

            # Update covalent executor config based on Terraform output
            self._update_config(tf_executor_config_file)

            # terraform_log_file = self._terraform_log_env_vars["TF_LOG_PATH"]
            # if Path(terraform_log_file).exists():
            #     Path(terraform_log_file).unlink()

            return cmd_output

    def down(self, print_callback: Callable) -> None:
        """
        Teardown previously spun up executor resources with terraform.

        Args:
            print_callback: Callback function to print output.

        Returns:
            None

        """
        terraform = self._get_tf_path()
        tf_state_file = self._get_tf_statefile_path()
        tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"

        tf_destroy = " ".join(["TF_CLI_ARGS=-no-color", terraform, "destroy", "-auto-approve"])

        # Run `terraform destroy`
        cmd_output = self._run_in_subprocess(
            cmd=tf_destroy,
            workdir=self.executor_tf_path,
            print_callback=print_callback,
            env_vars=self._terraform_log_env_vars,
        )

        if Path(tfvars_file).exists():
            Path(tfvars_file).unlink()

        terraform_log_file = self._terraform_log_env_vars["TF_LOG_PATH"]
        if Path(terraform_log_file).exists():
            Path(terraform_log_file).unlink()

        if Path(tf_state_file).exists():
            Path(tf_state_file).unlink()
            Path(f"{tf_state_file}.backup").unlink()

        return cmd_output

    def status(self) -> None:
        """
        Get the status of the spun up executor resources

        TODO: Return the list of resources being managed by terraform, i.e.
        if empty, then either the resources have not been created or
        have been destroyed already.

        Args:
            None

        Returns:
            None

        """
        terraform = self._get_tf_path()
        tf_state_file = self._get_tf_statefile_path()

        tf_state = " ".join([terraform, "state", "list", f"-state={tf_state_file}"])

        # Run `terraform state list`
        return self._run_in_subprocess(cmd=tf_state, workdir=self.executor_tf_path)
