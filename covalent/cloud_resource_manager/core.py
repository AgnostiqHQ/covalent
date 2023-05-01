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


import os
import shutil
import subprocess
from configparser import ConfigParser
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from covalent._shared_files.config import set_config
from covalent._shared_files.exceptions import CommandNotFoundError


class DeployStatus(Enum):
    """
    Status of the terraform deployment
    """

    OK = 0
    DESTROYED = 1
    ERROR = 2


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
            Path(executor_module_path).expanduser().resolve() / "terraform"
        )
        self.executor_options = options

    def _print_stdout(self, process: subprocess.Popen) -> Optional[int]:
        """
        Print the stdout from the subprocess to console

        Args:
            process: Python subprocess whose stdout is to be printed to screen

        Returns:
            returncode of the process
        """
        while process.poll() is None:
            if proc_stdout := process.stdout.readline():
                print(proc_stdout.strip().decode("utf-8"))
            else:
                break
        return process.poll()

    def _run_in_subprocess(
        self, cmd: str, workdir: str, env_vars: Optional[Dict[str, str]] = None
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
        retcode = self._print_stdout(proc)

        if retcode != 0:
            raise subprocess.CalledProcessError(returncode=retcode, cmd=cmd)

    def _update_config(self, tf_executor_config_file: str) -> None:
        """
        Update covalent configuration with the executor
        config values as obtained from terraform
        """
        executor_config = ConfigParser()
        executor_config.read(tf_executor_config_file)
        for key in executor_config[self.executor_name]:
            value = executor_config[self.executor_name][key]
            set_config({f"executors.{self.executor_name}.{key}": value})

    def _get_tf_path(self) -> str:
        """
        Get the terraform path
        """
        if terraform := shutil.which("terraform"):
            return terraform
        else:
            raise CommandNotFoundError("Terraform not found on system")

    def up(self, dry_run: bool = True):
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
                    f.write(f'{key}="{value}"\n')

        # Run `terraform plan`
        self._run_in_subprocess(
            cmd=tf_plan, workdir=self.executor_tf_path, env_vars=tf_vars_env_dict
        )

        # Create infrastructure as per the plan
        # Run `terraform apply`
        if not dry_run:
            self._run_in_subprocess(
                cmd=tf_apply, workdir=self.executor_tf_path, env_vars=tf_vars_env_dict
            )

            # Update covalent executor config based on Terraform output
            self._update_config(tf_executor_config_file)

    def down(self, dry_run: bool = True):
        """
        Teardown executor resources
        """
        if not dry_run:
            terraform = self._get_tf_path()

            tfvars_file = Path(self.executor_tf_path) / "terraform.tfvars"

            tf_destroy = " ".join([terraform, "destroy", "-auto-approve"])

            # Run `terraform destroy`
            self._run_in_subprocess(cmd=tf_destroy, workdir=self.executor_tf_path)

            if Path(tfvars_file).exists():
                Path(tfvars_file).unlink()

    def status(self):
        """
        Return executor resource deployment status
        """
        terraform = self._get_tf_path()

        tf_state = " ".join([terraform, "state", "list"])

        # Run `terraform state list`
        self._run_in_subprocess(cmd=tf_state, workdir=self.executor_tf_path)
