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


import asyncio
import os
import shutil
from typing import Dict, Optional

from covalent._shared_files.exceptions import CommandNotFoundError
from covalent._shared_files.logger import app_log


class ChangeDir(object):
    """
    Change directory context manager
    """

    def __init__(self, dir_to_change: str):
        self._pwd = os.getcwd()
        self._dir = dir_to_change

    def __enter__(self):
        os.chdir(self._dir)

    def __exit__(self, type, value, traceback):
        os.chdir(self._pwd)


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
        self.executor_module_path = executor_module_path
        self.executor_options = options

    async def up(self):
        """
        Setup executor resources
        """
        terraform = shutil.which("terraform")
        if not terraform:
            raise CommandNotFoundError("Terraform not found on system")

        executor_infra_assets_path = os.path.join(self.executor_module_path, "assets/infra")
        with ChangeDir(executor_infra_assets_path):
            proc = await asyncio.create_subprocess_exec(
                " ".join([terraform, "init"]),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await proc.communicate()
            if stdout:
                app_log.debug(f"{self.executor_name} stdout: {stdout}")
            if stderr:
                app_log.debug(f"{self.executor_name} stderr: {stdout}")

            # Setup TF_VAR environment variables by appending new variables to existing os.environ
            tf_var_env_dict = os.environ.copy()
            if self.executor_options:
                for key, value in self.executor_options.items():
                    tf_var_env_dict[f"TF_VAR_{key}"] = value

            proc = await asyncio.create_subprocess_shell(
                " ".join([terraform, "apply", "--auto-approve"]),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=tf_var_env_dict,
            )

            stdout, stderr = await proc.communicate()
            if stdout:
                app_log.debug(f"{self.executor_name} stdout: {stdout}")
            if stderr:
                app_log.debug(f"{self.executor_name} stderr: {stdout}")

    async def down(self):
        """
        Teardown executor resources
        """
        pass

    async def status(self):
        """
        Return executor resource deployment status
        """
        pass
