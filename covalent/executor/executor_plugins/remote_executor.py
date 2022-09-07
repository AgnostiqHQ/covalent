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

"""
This is a plugin executor module that is loaded at runtime by defining its default attributes in _EXECUTOR_PLUGIN_DEFAULTS
and optionally overriding the attributes in its constructor.

This module contains a RemoteExecutor class that provides abstract methods for implementing other remote executors.
Executor classes that inherit from the RemoteExecutor class can perform task execution by connecting with a remote environment
via SSH or Slurm or by interfacing with compute services in various cloud environments such as AWS, Azure, and GCP.
"""

import asyncio
from abc import abstractmethod
from typing import Any, Dict, Tuple

from covalent._shared_files import logger
from covalent.executor.base import AsyncBaseExecutor

# The plugin class name must be given by the executor_plugin_name attribute:
EXECUTOR_PLUGIN_NAME = "RemoteExecutor"

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_EXECUTOR_PLUGIN_DEFAULTS = {
    "poll_freq": 15,
    "remote_cache": ".cache/covalent",
    "credentials_file": "",
}


class RemoteExecutor(AsyncBaseExecutor):
    """
    Async executor class that provides abstract methods for managing task execution on a remote machine.

    Attributes:
        poll_freq: Number of seconds to wait between polling for task status after a task has been submitted.
        remote_cache: Location where pickled inputs/outputs are stored.
        credentials_file: Location where credentials can be found.
    """

    def __init__(
        self,
        poll_freq: int = 15,
        remote_cache: str = "",
        credentials_file: str = "",
        **kwargs,
    ) -> None:

        super().__init__(**kwargs)

        self.poll_freq = poll_freq
        self.remote_cache = remote_cache
        self.credentials_file = credentials_file

    @abstractmethod
    async def _validate_credentials(self) -> bool:
        """
        Abstract method to validate user credentials.

        Return:
            bool: True if the user credentials are valid and false if otherwise.
        """
        pass

    @abstractmethod
    async def _upload_task(self) -> None:
        """
        Abstract method that uploads the pickled function to the remote cache.
        """
        pass

    @abstractmethod
    async def submit_task(self, task_metadata: Dict) -> Any:
        """
        Abstract method that invokes the task on the remote backend.

        Args:
            task_metadata: Dictionary of metadata for the task. Current keys are
                          `dispatch_id` and `node_id`.
        Return:
            task_uuid: Task UUID defined on the remote backend.
        """
        pass

    @abstractmethod
    async def get_status(self) -> Any:
        """
        Abstract method that returns the status of an electron by querying the remote backend.
        """
        pass

    @abstractmethod
    async def _poll_task(self) -> Any:
        """
        Abstract method that polls the remote backend until the status of a workflow's execution
        is either COMPLETED or FAILED.
        """
        pass

    @abstractmethod
    async def query_result(self) -> Any:
        """
        Abstract method that retrieves the pickled result from the remote cache.
        """

    @abstractmethod
    async def cancel(self) -> bool:
        """
        Abstract method that sends a cancellation request to the remote backend.
        """
        pass

    @staticmethod
    async def run_async_subprocess(cmd) -> Tuple:
        """
        Invokes an async subprocess to run a command.
        """

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        if stdout:
            app_log.debug(stdout)

        if stderr:
            app_log.debug(stderr)

        return proc, stdout, stderr
