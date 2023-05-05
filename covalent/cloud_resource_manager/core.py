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
from typing import Callable, Dict, Optional

from covalent._shared_files.config import set_config
from covalent._shared_files.exceptions import CommandNotFoundError
from covalent.executor import _executor_manager


def get_executor_module(executor_name: str):
    return importlib.import_module(
        _executor_manager.executor_plugins_map[executor_name].__module__
    )


def get_converted_value(value: str):
    """
    Convert the value to the appropriate type
    """
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    elif value.lower() == "null":
        return None
    elif value.isdigit():
        return int(value)
    elif value.replace(".", "", 1).isdigit():
        return float(value)
    else:
        return value


def validate_options(executor_options: Dict[str, str], executor_name: str):
    """
    Validate the options passed to the CRM
    """
    # Importing validation classes from the executor module
    module = get_executor_module(executor_name)
    ExecutorPluginDefaults = getattr(module, "ExecutorPluginDefaults")
    ExecutorInfraDefaults = getattr(module, "ExecutorInfraDefaults")

    # Validating the passed options:
    # TODO: What exactly are the options passed? Are they plugin defaults or infra defaults?

    plugin_attrs = list(ExecutorPluginDefaults.schema()["properties"].keys())
    infra_attrs = list(ExecutorInfraDefaults.schema()["properties"].keys())

    plugin_params = {k: v for k, v in executor_options.items() if k in plugin_attrs}
    infra_params = {k: v for k, v in executor_options.items() if k in infra_attrs}

    # Validate options
    ExecutorPluginDefaults(**plugin_params)
    ExecutorInfraDefaults(**infra_params)


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

        if self.executor_options:
            validate_options(self.executor_options, self.executor_name)

    def _print_stdout(
        self, process: subprocess.Popen, print_callback: Callable = None
    ) -> Optional[int]:
        """
        Print the stdout from the subprocess to console

        Args:
            process: Python subprocess whose stdout is to be printed to screen

        Returns:
            returncode of the process
        """
        while process.poll() is None and (proc_stdout := process.stdout.readline()):
            if print_callback:
                print_callback(proc_stdout.strip().decode("utf-8"))
        return process.poll()

    def _run_in_subprocess(
        self,
        cmd: str,
        workdir: str,
        print_callback: Callable = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Optional[int]:
        """
        Run the `cmd` in a subprocess shell with the env_vars set in the process's new environment

        Args:
            cmd: Command to execute in the subprocess
            workdir: Working directory of the subprocess
            env_vars: Dictionary of environment variables to set in the processes execution environment

        Returns:
            Exit code of the process
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
            raise subprocess.CalledProcessError(returncode=retcode, cmd=cmd)

    def _update_config(self, tf_executor_config_file: str) -> None:
        """
        Update covalent configuration with the executor
        config values as obtained from terraform
        """

        # Puts the plugin options in covalent's config
        executor_config = ConfigParser()
        executor_config.read(tf_executor_config_file)
        for key in executor_config[self.executor_name]:
            value = executor_config[self.executor_name][key]
            converted_value = get_converted_value(value)
            set_config({f"executors.{self.executor_name}.{key}": converted_value})

    def _get_tf_path(self) -> str:
        """
        Get the terraform path
        """
        if terraform := shutil.which("terraform"):
            return terraform
        else:
            raise CommandNotFoundError("Terraform not found on system")

    def up(self, print_callback: Callable, dry_run: bool = True):
        """
        Setup executor resources
        """
        terraform = self._get_tf_path()

        tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"
        tf_executor_config_file = Path(self.executor_tf_path) / f"{self.executor_name}.conf"

        tf_init = " ".join([terraform, "init"])
        tf_plan = " ".join([terraform, "plan", "-out", "tf.plan"])
        tf_apply = " ".join([terraform, "apply", "tf.plan"])

        # Run `terraform init`
        self._run_in_subprocess(cmd=tf_init, workdir=self.executor_tf_path)

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
            env_vars=tf_vars_env_dict,
        )

        # Create infrastructure as per the plan
        # Run `terraform apply`
        if not dry_run:
            cmd_output = self._run_in_subprocess(
                cmd=tf_apply,
                workdir=self.executor_tf_path,
                env_vars=tf_vars_env_dict,
                print_callback=print_callback,
            )

            # Update covalent executor config based on Terraform output
            self._update_config(tf_executor_config_file)

            return cmd_output

    def down(self, print_callback: Callable):
        """
        Teardown executor resources
        """
        terraform = self._get_tf_path()

        tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"

        tf_destroy = " ".join([terraform, "destroy", "-auto-approve"])

        # Run `terraform destroy`
        cmd_output = self._run_in_subprocess(
            cmd=tf_destroy, workdir=self.executor_tf_path, print_callback=print_callback
        )

        if Path(tfvars_file).exists():
            Path(tfvars_file).unlink()

        return cmd_output

    def status(self):
        """
        Return the list of resources being managed by terraform, i.e.
        if empty, then either the resources have not been created or
        have been destroyed already.
        """
        terraform = self._get_tf_path()

        tf_state = " ".join([terraform, "state", "list"])

        # Run `terraform state list`
        return self._run_in_subprocess(cmd=tf_state, workdir=self.executor_tf_path)


# if __name__ == "__main__":

#     executor_module_path = Path(
#         __import__(_executor_manager.executor_plugins_map["awsbatch"].__module__).__path__[0]
#     )


#     crm = CloudResourceManager(
#         executor_name="awsbatch",
#         executor_module_path=executor_module_path,
#         options={
#             "prefix": "sankalp",
#         }
#     )

#     crm.up(dry_run=False)

#     time.sleep(2)

#     crm.status()

#     time.sleep(2)

#     crm.down(dry_run=False)
