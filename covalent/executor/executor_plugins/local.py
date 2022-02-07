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
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

# Relative imports are not allowed in executor plugins
from covalent._shared_files import logger
from covalent._shared_files.util_classes import DispatchInfo
from covalent._workflow.transport import TransportableObject
from covalent.executor import BaseExecutor

# The plugin class name must be given by the executor_plugin_name attribute:
executor_plugin_name = "LocalExecutor"

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

    def execute(
        self,
        function: TransportableObject,
        kwargs: Any,
        execution_args: dict,
        dispatch_id: str,
        node_id: int = -1,
    ) -> Any:
        """
        Executes the input function and returns the result.

        Args:
            function: The input python function which will be executed and whose result
                      is ultimately returned by this function.
            kwargs: Keyword arguments to be used by function.
            execution_args: Executor-specific arguments.
            dispatch_id: The unique identifier of the external lattice process which is
                         calling this function.
            node_id: The node ID of this task in the bigger workflow graph.

        Returns:
            output: The result of the executed function.
        """

        dispatch_info = DispatchInfo(dispatch_id)

        with self.get_dispatch_context(dispatch_info), redirect_stdout(
            io.StringIO()
        ) as stdout, redirect_stderr(io.StringIO()) as stderr:

            if self.conda_env != "":
                # Extract any executor-specific bash commands from execution_args that are
                # needed. Each command should be an entry in executor_specific_execution_args.
                # This executor has none.
                executor_specific_exec_cmds = []
                result = self.execute_in_conda_env(
                    function,
                    kwargs,
                    execution_args,
                    executor_specific_exec_cmds,
                    dispatch_info,
                    self.conda_env,
                    self.cache_dir,
                    node_id,
                )

            else:
                fn = function.get_deserialized()
                result = fn(**kwargs)

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            execution_args["results_dir"],
        )

        return (result, stdout.getvalue(), stderr.getvalue())
