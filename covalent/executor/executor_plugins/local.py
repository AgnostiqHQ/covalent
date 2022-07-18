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
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Dict, List, Tuple

# Relative imports are not allowed in executor plugins
from covalent._shared_files import logger
from covalent._shared_files.util_classes import DispatchInfo
from covalent._workflow.transport import TransportableObject
from covalent.executor import BaseExecutor

# The plugin class name must be given by the executor_plugin_name attribute:
executor_plugin_name = "LocalExecutor"

app_log = logger.app_log
log_stack_info = logger.log_stack_info

_EXECUTOR_PLUGIN_DEFAULTS = {
    "log_stdout": "stdout.log",
    "log_stderr": "stderr.log",
    "cache_dir": os.path.join(
        os.environ.get("XDG_CACHE_HOME") or os.path.join(os.environ["HOME"], ".cache"), "covalent"
    ),
}


def wrapper_fn(
    function: TransportableObject,
    call_before: List[Tuple[TransportableObject, TransportableObject, TransportableObject]],
    call_after: List[Tuple[TransportableObject, TransportableObject, TransportableObject]],
    *args,
    **kwargs,
):
    """Wrapper for serialized callable.

    Execute preparatory shell commands before deserializing and
    running the callable. This is the actual function to be sent to
    the various executors.

    """

    app_log.debug("Invoking call_before")
    cb_retvals = {}
    for tup in call_before:
        serialized_fn, serialized_args, serialized_kwargs, retval_key = tup
        cb_fn = serialized_fn.get_deserialized()
        cb_args = serialized_args.get_deserialized()
        cb_kwargs = serialized_kwargs.get_deserialized()
        app_log.debug(f"Invoking ({cb_fn}, args={cb_args}, kwargs={cb_kwargs}")
        retval = cb_fn(*cb_args, **cb_kwargs)
        if retval_key:
            cb_retvals[retval_key] = retval

    app_log.debug(f"Serialized args: {args}, kwargs: {kwargs}")
    new_args = [arg.get_deserialized() for arg in args]
    new_kwargs = {k: v.get_deserialized() for k, v in kwargs.items()}

    fn = function.get_deserialized()

    # Inject return values into kwargs
    for key, val in cb_retvals.items():
        new_kwargs[key] = val
        app_log.debug(f"Injecting argument {key}")

    app_log.debug(f"Invoking {fn}, {new_args}, {new_kwargs}")
    output = fn(*new_args, **new_kwargs)

    app_log.debug("Invoking call_after")
    for tup in call_after:
        serialized_fn, serialized_args, serialized_kwargs, retval_key = tup
        ca_fn = serialized_fn.get_deserialized()
        ca_args = serialized_args.get_deserialized()
        ca_kwargs = serialized_kwargs.get_deserialized()
        app_log.debug(f"Invoking ({ca_fn}, args={ca_args}, kwargs={ca_kwargs}")
        ca_fn(*ca_args, **ca_kwargs)

    return TransportableObject(output)


class LocalExecutor(BaseExecutor):
    """
    Local executor class that directly invokes the input function.
    """

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
                result = wrapper_fn(*new_args, **kwargs)

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, stdout.getvalue(), stderr.getvalue())
