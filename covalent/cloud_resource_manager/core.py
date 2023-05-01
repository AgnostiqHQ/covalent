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


def is_int(value: str) -> bool:
    """
    Check if the string passed is int convertible
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value: str) -> bool:
    """
    Check if string is convertible to float
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


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
        self.executor_tf_path = os.path.join(executor_module_path, "assets/infra")
        self.executor_options = options

    @staticmethod
    def _print_stdout(process: subprocess.Popen) -> Optional[int]:
        """
        Print the stdout from the subprocess to console
        Arg(s)
            process: Python subprocess whose stdout is to be printed to screen
        Return(s)
            None
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
        Arg(s)
            cmd: Command to execute in the subprocess
            workdir: Working directory of the subprocess
            env_vars: Dictionary of environment variables to set in the processes execution environment
        Return(s)
            Exit code of the process
        """
        proc = subprocess.Popen(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=workdir,
            shell=True,
            bufsize=-1,
            env=env_vars,
        )
        retcode = self._print_stdout(proc)
        return retcode

    def _update_config(self, tf_executor_config_file: str) -> None:
        """
        Update covalent configuration with the executor values
        """
        executor_config = ConfigParser()
        executor_config.read(tf_executor_config_file)
        for key in executor_config[self.executor_name]:
            value = executor_config[self.executor_name][key]
            converted_value = (
                int(value) if is_int(value) else float(value) if is_float(value) else value
            )
            set_config({f"executors.{self.executor_name}.{key}": converted_value})

    def up(self, dry_run: bool = True):
        """
        Setup executor resources
        """
        terraform = shutil.which("terraform")
        if not terraform:
            raise CommandNotFoundError("Terraform not found on system")

        tfvars_file = os.path.join(self.executor_tf_path, "terraform.tfvars")
        tf_executor_config_file = os.path.join(self.executor_tf_path, f"{self.executor_name}.conf")

        tf_init = " ".join([terraform, "init"])
        tf_plan = " ".join([terraform, "plan", "-out", "tf.plan"])
        tf_apply = " ".join([terraform, "apply", "tf.plan"])

        retcode = self._run_in_subprocess(cmd=tf_init, workdir=self.executor_tf_path)
        if retcode != 0:
            raise subprocess.CalledProcessError(returncode=retcode, cmd=tf_init)

        # Setup terraform infra variables as passed by the user
        tf_vars_env_dict = os.environ.copy()
        if self.executor_options:
            with open(tfvars_file, "w") as f:
                for key, value in self.executor_options.items():
                    tf_vars_env_dict[f"TF_VAR_{key}"] = value
                    f.write(f'{key}="{value}"\n')

        # Plan the infrastructure
        retcode = self._run_in_subprocess(
            cmd=tf_plan, workdir=self.executor_tf_path, env_vars=tf_vars_env_dict
        )
        if retcode != 0:
            raise subprocess.CalledProcessError(returncode=retcode, cmd=tf_plan)

        # Create infrastructure as per the plan
        if not dry_run:
            retcode = self._run_in_subprocess(
                cmd=tf_apply, workdir=self.executor_tf_path, env_vars=tf_vars_env_dict
            )
            if retcode != 0:
                raise subprocess.CalledProcessError(returncode=retcode, cmd=tf_apply)

            # Update covalent executor config based on Terraform output
            self._update_config(tf_executor_config_file)

    def down(self, dry_run: bool = True):
        """
        Teardown executor resources
        """
        terraform = shutil.which("terraform")
        if not terraform:
            raise CommandNotFoundError("Terraform not found on system")

        if not dry_run:
            tfvars_file = os.path.join(self.executor_tf_path, "terraform.tfvars")

            tf_destroy = " ".join([terraform, "destroy", "-auto-approve"])
            retcode = self._run_in_subprocess(cmd=tf_destroy, workdir=self.executor_tf_path)
            if retcode != 0:
                raise subprocess.CalledProcessError(cmd=tf_destroy, returncode=retcode)

            if os.path.exists(tfvars_file):
                os.remove(tfvars_file)

    def status(self):
        """
        Return executor resource deployment status
        """
        pass
