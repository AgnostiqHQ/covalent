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
Module for defining a Dask executor that submits the input python function in a dask cluster
and waits for execution to finish then returns the result.

This is a plugin executor module; it is loaded if found and properly structured.
"""

import asyncio
import io
import os
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Callable, Dict, List

from dask.distributed import Client, get_client

from covalent._shared_files import logger

# Relative imports are not allowed in executor plugins
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import DispatchInfo
from covalent._shared_files.utils import _address_client_mapper
from covalent.executor import BaseAsyncExecutor

# The plugin class name must be given by the executor_plugin_name attribute:
executor_plugin_name = "DaskExecutor"

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_EXECUTOR_PLUGIN_DEFAULTS = {
    "log_stdout": "stdout.log",
    "log_stderr": "stderr.log",
    "cache_dir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"), "covalent"
    ),
}


class DaskExecutor(BaseAsyncExecutor):
    """
    Dask executor class that submits the input function to a running dask cluster.
    """

    def __init__(
        self,
        scheduler_address: str = "",
        log_stdout: str = "stdout.log",
        log_stderr: str = "stderr.log",
        conda_env: str = "",
        cache_dir: str = "",
        current_env_on_conda_fail: bool = False,
    ) -> None:
        if not cache_dir:
            cache_dir = os.path.join(
                os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"),
                "covalent",
            )

        if not scheduler_address:
            scheduler_address = get_config("dask.scheduler_address")

        super().__init__(log_stdout, log_stderr, conda_env, cache_dir, current_env_on_conda_fail)

        self.scheduler_address = scheduler_address

    async def execute(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:
        """
        Executes the input function and returns the result.

        Args:
            function: The input python function which will be executed and whose result
                      is ultimately returned by this function.
            args: List of positional arguments to be used by the function.
            kwargs: Dictionary of keyword arguments to be used by the function.
            dispatch_id: The unique identifier of the external lattice process which is
                         calling this function.
            results_dir: The location of the results directory.
            node_id: The node ID of this task in the bigger workflow graph.

        Returns:
            output: The result of the executed function.
        """

        dask_client = _address_client_mapper.get(self.scheduler_address)

        if dask_client and not dask_client.scheduler:
            await dask_client

        if not dask_client or not dask_client.scheduler:
            dask_client = Client(address=self.scheduler_address, timeout=2, asynchronous=True)
            _address_client_mapper[self.scheduler_address] = dask_client

            await dask_client

        dispatch_info = DispatchInfo(dispatch_id)

        with self.get_dispatch_context(dispatch_info), redirect_stdout(
            io.StringIO()
        ) as stdout, redirect_stderr(io.StringIO()) as stderr:

            future = dask_client.submit(function, *args, **kwargs)
            result = await dask_client.gather(future)

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, stdout.getvalue(), stderr.getvalue())
