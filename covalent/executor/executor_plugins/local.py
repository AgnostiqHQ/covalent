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
Module for defining a local executor that directly invokes the input python function.

This is a plugin executor module; it is loaded if found and properly structured.
"""

import io
import os
from contextlib import redirect_stderr, redirect_stdout
from multiprocessing import Queue as MPQ
from typing import Any, Dict, List

# Relative imports are not allowed in executor plugins
from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.util_classes import DispatchInfo
from covalent._workflow.transport import TransportableObject
from covalent.executor import BaseExecutor

# The plugin class name must be given by the EXECUTOR_PLUGIN_NAME attribute:
EXECUTOR_PLUGIN_NAME = "LocalExecutor"

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_EXECUTOR_PLUGIN_DEFAULTS = {
    "log_stdout": "stdout.log",
    "log_stderr": "stderr.log",
    "cache_dir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"), "covalent"
    ),
}


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.

    Args:
        log_stdout: The path to the file to be used for redirecting stdout.
        log_stderr: The path to the file to be used for redirecting stderr.
        cache_dir: The location used for cached files in the executor.
        kwargs: Key-word arguments to be passed to the parent class (BaseExecutor)
    """

    def __init__(
        self,
        log_stdout: str = "stdout.log",
        log_stderr: str = "stderr.log",
        cache_dir: str = os.path.join(
            os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"),
            "covalent",
        ),
        **kwargs,
    ):
        self.log_stdout = log_stdout
        self.log_stderr = log_stderr
        self.cache_dir = cache_dir

        base_kwargs = {"cache_dir": self.cache_dir}
        for key in kwargs:
            if key in [
                "conda_env",
                "current_env_on_conda_fail",
            ]:
                base_kwargs[key] = kwargs[key]

        super().__init__(**base_kwargs)

    def execute(
        self,
        function: TransportableObject,
        args: List,
        kwargs: Dict,
        info_queue: MPQ,
        task_id: int,
        dispatch_id: str,
        results_dir: str,
    ) -> Any:
        """
        Executes the input function and returns the result.

        Args:
            function: The input python function which will be executed and whose result
                      is ultimately returned by this function.
            args: List of positional arguments to be used by the function.
            kwargs: Dictionary of keyword arguments to be used by the function.
            info_queue: A multiprocessing Queue object used for shared variables across
                processes. Information about, eg, status, can be stored here.
            task_id: The ID of this task in the bigger workflow graph.
            dispatch_id: The unique identifier of the external lattice process which is
                         calling this function.
            results_dir: The location of the results directory.

        Returns:
            output: The result of the executed function.
        """

        dispatch_info = DispatchInfo(dispatch_id)
        fn = function.get_deserialized()
        fn_version = function.python_version

        exception = None

        info_dict = {"STATUS": Result.RUNNING}
        info_queue.put_nowait(info_dict)

        with self.get_dispatch_context(dispatch_info), redirect_stdout(
            io.StringIO()
        ) as stdout, redirect_stderr(io.StringIO()) as stderr:

            result = None
            if self.conda_env != "":

                result, exception = self.execute_in_conda_env(
                    fn,
                    fn_version,
                    args,
                    kwargs,
                    self.conda_env,
                    self.cache_dir,
                    info_queue,
                    task_id,
                )

            else:
                try:
                    result = fn(*args, **kwargs)
                except Exception as e:
                    exception = e

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        info_dict = info_queue.get()
        info_dict["STATUS"] = Result.FAILED if result is None else Result.COMPLETED
        info_queue.put(info_dict)

        return (result, stdout.getvalue(), stderr.getvalue(), exception)

    def get_status(self, info_dict: dict) -> Result:
        """
        Get the current status of the task.

        Args:
            info_dict: a dictionary containing any neccessary parameters needed to query the
                status. For this class (LocalExecutor), the only info is given by the
                "STATUS" key in info_dict.

        Returns:
            A Result status object (or None, if "STATUS" is not in info_dict).
        """

        return info_dict.get("STATUS", Result.NEW_OBJ)
