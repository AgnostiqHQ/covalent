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

import io
import os
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict, List

from dask.distributed import get_client

from covalent._shared_files import logger

# Relative imports are not allowed in executor plugins
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import DispatchInfo
from covalent._workflow.transport import TransportableObject
from covalent.executor import BaseExecutor, wrapper_fn

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


class DaskExecutor(BaseExecutor):
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

        if scheduler_address == "":
            try:
                scheduler_address = get_config("dask.scheduler_address")
            except KeyError as ex:
                app_log.debug(
                    "No dask scheduler address found in config. Address must be set manually."
                )

        super().__init__(log_stdout, log_stderr, conda_env, cache_dir, current_env_on_conda_fail)

        self.scheduler_address = scheduler_address

    def execute(
        self,
        function: TransportableObject,
        args: List,
        kwargs: Dict,
        call_before: List,
        call_after: List,
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

        dask_client = get_client(address=self.scheduler_address, timeout=1)

        dispatch_info = DispatchInfo(dispatch_id)

        fn_version = function.python_version

        new_args = [function, call_before, call_after]
        for arg in args:
            new_args.append(arg)

        with self.get_dispatch_context(dispatch_info), redirect_stdout(
            io.StringIO()
        ) as stdout, redirect_stderr(io.StringIO()) as stderr:

            if self.conda_env != "":
                result = None

                result = self.execute_in_conda_env(
                    wrapper_fn,
                    fn_version,
                    new_args,
                    kwargs,
                    self.conda_env,
                    self.cache_dir,
                    node_id,
                )

            else:
                future = dask_client.submit(wrapper_fn, *new_args, **kwargs)
                result = future.result()

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, stdout.getvalue(), stderr.getvalue())
