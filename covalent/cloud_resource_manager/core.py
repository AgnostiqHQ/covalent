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


import importlib
import logging
import os
import shutil
import subprocess
import sys
from configparser import ConfigParser
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, List, Optional, Union

from covalent._shared_files.config import set_config
from covalent.executor import _executor_manager

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)
logger.propagate = False


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
            try:
                settings_dict[key]["value"] = value
            except:
                logger.error(f"No such option '{key}'. Use --help for available options")
                sys.exit()

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
            "TF_LOG_PATH": os.path.join(self.executor_tf_path, "terraform-error.log"),
            "PATH": "$PATH:/usr/bin",
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
        with open(Path(self.executor_tf_path) / "terraform-error.log", "r", encoding="UTF-8") as f:
            lines = f.readlines()
        for _, line in enumerate(lines):
            error_index = line.strip().find("error:")
            if error_index != -1:
                error_message = line.strip()[error_index + len("error:") :]
                logger.error(error_message)
        return lines

    def _terraform_error_validator(self, tfstate_path: str) -> bool:
        """
        Terraform error validator checks whether any terraform-error.log files existence and validate last line.
        Args: None
        Return:
            up    - if terraform-error.log is empty and tfstate exists.
            *up   - if terraform-error.log is not empty and 'On deploy' at last line.
            down  - if terraform-error.log is empty and tfstate file not exists.
            *down - if terraform-error.log is not empty and 'On destroy' at last line.
        """
        tf_error_file = os.path.join(self.executor_tf_path, "terraform-error.log")
        if os.path.exists(tf_error_file) and os.path.getsize(tf_error_file) > 0:
            with open(tf_error_file, "r", encoding="UTF-8") as error_file:
                indicator = error_file.readlines()[-1]
                if indicator == "On deploy":
                    return "*up"
                elif indicator == "On destroy":
                    return "*down"
        return "up" if os.path.exists(tfstate_path) else "down"

    def _get_resource_status(
        self,
        proc: subprocess.Popen,
        cmd: str,
    ) -> str:
        """
        Get resource status will return current status of plugin based on terraform-error.log and tfstate file.
        Args:
            proc  : subprocess.Popen - To read stderr from Popen.communicate.
            cmd   : command for executing terraform scripts.
        Returns:
            status: str - status of plugin
        """
        _, stderr = proc.communicate()
        cmds = cmd.split(" ")
        tfstate_path = cmds[-1].split("=")[-1]
        if stderr is None:
            return self._terraform_error_validator(tfstate_path=tfstate_path)
        else:
            raise subprocess.CalledProcessError(
                returncode=1, cmd=cmd, stderr=self._parse_terraform_error_log()
            )

    def _log_error_msg(self, cmd) -> None:
        """
        Log error msg with valid command to terraform-erro.log
        Args: cmd: str - terraform-error.log file path.
        """
        with open(
            Path(self.executor_tf_path) / "terraform-error.log", "a", encoding="UTF-8"
        ) as file:
            if any(tf_cmd in cmd for tf_cmd in ["init", "plan", "apply"]):
                file.write("\nOn deploy")
            elif "destroy" in cmd:
                file.write("\nOn destroy")

    def _run_in_subprocess(
        self,
        cmd: str,
        workdir: str,
        env_vars: Optional[Dict[str, str]] = None,
        print_callback: Optional[Callable] = None,
    ) -> Union[None, str]:
        """
        Run the `cmd` in a subprocess shell with the env_vars set in the process's new environment

        Args:
            cmd: Command to execute in the subprocess
            workdir: Working directory of the subprocess
            env_vars: Dictionary of environment variables to set in the processes execution environment

        Returns:
            Union[None, str]
                - For 'covalent deploy status'
                    returns status of the deplyment
                - Others
                    return None
        """
        if git := shutil.which("git"):
            proc = subprocess.Popen(
                args=cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=workdir,
                shell=True,
                env=env_vars,
            )
            TERRAFORM_STATE = "state list -state"
            if TERRAFORM_STATE in cmd:
                return self._get_resource_status(proc=proc, cmd=cmd)
            retcode = self._print_stdout(proc, print_callback)

            if retcode != 0:
                self._log_error_msg(cmd=cmd)
                raise subprocess.CalledProcessError(
                    returncode=retcode, cmd=cmd, stderr=self._parse_terraform_error_log()
                )
        else:
            self._log_error_msg(cmd=cmd)
            logger.error("Git not found on the system.")
            sys.exit()

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

    def _validation_docker(self) -> None:
        if not shutil.which("docker"):
            logger.error("Docker not found on system")
            sys.exit()

    def _get_tf_path(self) -> str:
        """
        Get the terraform path

        Args:
            None

        Returns:
            Path to terraform executable

        """
        if terraform := shutil.which("terraform"):
            result = subprocess.run(
                ["terraform --version"], shell=True, capture_output=True, text=True
            )
            version = result.stdout.split("v", 1)[1][:3]
            if float(version) < 1.4:
                logger.error(
                    "Old version of terraform found. Please update it to version greater than 1.3"
                )
                sys.exit()
            return terraform
        else:
            logger.error("Terraform not found on system")
            exit()

    def _get_tf_statefile_path(self) -> str:
        """
        Get the terraform state file path

        Args:
            None

        Returns:
            Path to terraform state file

        """
        # Saving in a directory which doesn't get deleted on purge
        return str(Path(self.executor_tf_path) / "terraform.tfstate")

    def up(self, print_callback: Callable, dry_run: bool = True) -> None:
        """
        Spin up executor resources with terraform

        Args:
            dry_run: If True, only run terraform plan and not apply

        Returns:
            None

        """
        terraform = self._get_tf_path()
        self._validation_docker()
        tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"
        tf_executor_config_file = Path(self.executor_tf_path) / f"{self.executor_name}.conf"

        tf_init = " ".join([terraform, "init"])
        tf_plan = " ".join([terraform, "plan", "-out", "tf.plan"])
        tf_apply = " ".join([terraform, "apply", "tf.plan"])
        terraform_log_file = self._terraform_log_env_vars["TF_LOG_PATH"]

        if Path(terraform_log_file).exists():
            Path(terraform_log_file).unlink()

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
            env_vars=self._terraform_log_env_vars,
            print_callback=print_callback,
        )

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

        if Path(terraform_log_file).exists() and os.path.getsize(terraform_log_file) == 0:
            Path(terraform_log_file).unlink()

    def down(self, print_callback: Callable) -> None:
        """
        Teardown previously spun up executor resources with terraform.

        Args:
            print_callback: Callback function to print output.

        Returns:
            None

        """
        terraform = self._get_tf_path()
        self._validation_docker()
        tf_state_file = self._get_tf_statefile_path()
        tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"
        terraform_log_file = self._terraform_log_env_vars["TF_LOG_PATH"]

        tf_destroy = " ".join(
            [
                "TF_CLI_ARGS=-no-color",
                "TF_LOG=ERROR",
                f"TF_LOG_PATH={terraform_log_file}",
                terraform,
                "destroy",
                "-auto-approve",
            ]
        )
        if Path(terraform_log_file).exists():
            Path(terraform_log_file).unlink()

        # Run `terraform destroy`
        self._run_in_subprocess(
            cmd=tf_destroy,
            workdir=self.executor_tf_path,
            print_callback=print_callback,
            env_vars=self._terraform_log_env_vars,
        )

        if Path(tfvars_file).exists():
            Path(tfvars_file).unlink()

        if Path(terraform_log_file).exists() and os.path.getsize(terraform_log_file) == 0:
            Path(terraform_log_file).unlink()

        if Path(tf_state_file).exists():
            Path(tf_state_file).unlink()
            if Path(f"{tf_state_file}.backup").exists():
                Path(f"{tf_state_file}.backup").unlink()

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
        self._validation_docker()
        tf_state_file = self._get_tf_statefile_path()

        tf_state = " ".join([terraform, "state", "list", f"-state={tf_state_file}"])

        # Run `terraform state list`
        return self._run_in_subprocess(
            cmd=tf_state, workdir=self.executor_tf_path, env_vars=self._terraform_log_env_vars
        )
