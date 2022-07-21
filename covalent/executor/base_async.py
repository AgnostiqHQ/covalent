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
Class that defines the base async executor template.
"""

import io
from abc import abstractmethod
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Callable, Dict, List

from .._shared_files import logger
from .._shared_files.util_classes import DispatchInfo
from .base import BaseExecutor

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class BaseAsyncExecutor(BaseExecutor):
    """
    Async base executor class to be used for defining any executor
    plugin. Subclassing this class will allow you to define
    your own executor plugin which can be used in covalent.

    Note: When using a conda environment, it is assumed that
    covalent with all its dependencies are also installed in
    that environment.

    Attributes:
        log_stdout: The path to the file to be used for redirecting stdout.
        log_stderr: The path to the file to be used for redirecting stderr.
        conda_env: The name of the Conda environment to be used.
        cache_dir: The location used for cached files in the executor.
        current_env_on_conda_fail: If True, the current environment will be used
                                   if conda fails to activate specified env.
    """

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
        Execute the function with the given arguments.

        This calls the executor-specific `run()` method in an async-aware manner.

        Args:
            function: The input python function which will be executed and whose result
                      is ultimately returned by this function.
            args: List of positional arguments to be used by the function.
            kwargs: Dictionary of keyword arguments to be used by the function.
            dispatch_id: The unique identifier of the external lattice process which is
                         calling this function.
            results_dir: The location of the results directory.
            node_id: ID of the node in the transport graph which is using this executor.

        Returns:
            output: The result of the function execution.
        """

        dispatch_info = DispatchInfo(dispatch_id)
        fn_version = function.args[0].python_version

        with self.get_dispatch_context(dispatch_info), redirect_stdout(
            io.StringIO()
        ) as stdout, redirect_stderr(io.StringIO()) as stderr:

            if self.conda_env != "":
                result = None

                result = self.execute_in_conda_env(
                    function,
                    fn_version,
                    args,
                    kwargs,
                    self.conda_env,
                    self.cache_dir,
                    node_id,
                )

            else:
                result = await self.run(function, args, kwargs)

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, stdout.getvalue(), stderr.getvalue())

    @abstractmethod
    async def run(self, function: callable, args: List, kwargs: Dict) -> Any:
        """
        Abstract method to run a function in the executor in async-aware manner.

        Args:
            function: The function to run in the executor
            args: List of positional arguments to be used by the function
            kwargs: Dictionary of keyword arguments to be used by the function.

        Returns:
            output: The result of the function execution
        """

        raise NotImplementedError
