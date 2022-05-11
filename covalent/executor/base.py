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
Class that defines the base executor template.
"""

import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, ContextManager, Dict, Iterable, List, Tuple

import cloudpickle as pickle

from .._shared_files import logger
from .._shared_files.context_managers import active_dispatch_info_manager
from .._shared_files.util_classes import DispatchInfo
from .._workflow.transport import TransportableObject

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class BaseExecutor(ABC):
    """
    Base executor class to be used for defining any executor
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

    def __init__(
        self,
        log_stdout: str = "",
        log_stderr: str = "",
        conda_env: str = "",
        cache_dir: str = "",
        current_env_on_conda_fail: bool = False,
    ) -> None:
        self.log_stdout = log_stdout
        self.log_stderr = log_stderr
        self.conda_env = conda_env
        self.cache_dir = cache_dir
        self.current_env_on_conda_fail = current_env_on_conda_fail
        self.current_env = ""

    def get_dispatch_context(self, dispatch_info: DispatchInfo) -> ContextManager[DispatchInfo]:
        """
        Start a context manager that will be used to
        access the dispatch info for the executor.

        Args:
            dispatch_info: The dispatch info to be used inside current context.

        Returns:
            A context manager object that handles the dispatch info.
        """

        return active_dispatch_info_manager.claim(dispatch_info)

    def write_streams_to_file(
        self,
        stream_strings: Iterable[str],
        filepaths: Iterable[str],
        dispatch_id: str,
        results_dir: str,
    ) -> None:
        """
        Write the contents of stdout and stderr to respective files.

        Args:
            stream_strings: The stream_strings to be written to files.
            filepaths: The filepaths to be used for writing the streams.
            dispatch_id: The ID of the dispatch which initiated the request.
            results_dir: The location of the results directory.
        """

        for ss, filepath in zip(stream_strings, filepaths):
            if filepath:
                # If it is a relative path, attach to results dir
                if not Path(filepath).expanduser().is_absolute():
                    filepath = os.path.join(results_dir, dispatch_id, filepath)

                filename = Path(filepath)
                filename = filename.expanduser()
                filename.parent.mkdir(parents=True, exist_ok=True)
                filename.touch(exist_ok=True)

                with open(filepath, "a") as f:
                    f.write(ss)
            else:
                print(ss)

    @abstractmethod
    async def execute(
        self,
        function: TransportableObject,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:
        """
        Execute the function with the given arguments.
        This will be overriden by other executor plugins
        to design how said function needs to be run.

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

        raise NotImplementedError

    def execute_in_conda_env(
        self,
        fn: Callable,
        fn_version: str,
        args: List,
        kwargs: Dict,
        conda_env: str,
        cache_dir: str,
        node_id: int,
    ) -> Tuple[bool, Any]:
        """
        Execute the function with the given arguments, in a Conda environment.

        Args:
            fn: The input python function which will be executed and whose result
                is ultimately returned by this function.
            fn_version: The python version the function was created with.
            args: List of positional arguments to be used by the function.
            kwargs: Dictionary of keyword arguments to be used by the function.
            conda_env: Name of a Conda environment in which to execute the task.
            cache_dir: The directory where temporary files and logs (if any) are stored.
            node_id: The integer identifier for the current node.

        Returns:
            output: The result of the function execution.
        """

        if not self.get_conda_path():
            return self._on_conda_env_fail(fn, args, kwargs, node_id)

        # Pickle the function
        temp_filename = ""
        with tempfile.NamedTemporaryFile(dir=cache_dir, delete=False) as f:
            pickle.dump(fn, f)
            temp_filename = f.name

        result_filename = os.path.join(cache_dir, f'result_{temp_filename.split("/")[-1]}')

        # Write a bash script to activate the environment
        shell_commands = "#!/bin/bash\n"

        # Add commands to initialize the Conda shell and activate the environment:
        conda_sh = os.path.join(
            os.path.dirname(self.conda_path), "..", "etc", "profile.d", "conda.sh"
        )
        conda_sh = os.environ.get("CONDA_SHELL", conda_sh)
        if os.path.exists(conda_sh):
            shell_commands += f"source {conda_sh}\n"
        else:
            message = "No Conda installation found on this compute node."
            app_log.warning(message)
            return self._on_conda_env_fail(fn, args, kwargs, node_id)

        shell_commands += f"conda activate {conda_env}\n"
        shell_commands += "retval=$?\n"
        shell_commands += "if [ $retval -ne 0 ]; then\n"
        shell_commands += (
            f'  echo "Conda environment {conda_env} is not present on this compute node."\n'
        )
        shell_commands += '  echo "Please create that environment (or use an existing environment) and try again."\n'
        shell_commands += "  exit 99\n"
        shell_commands += "fi\n\n"

        # Check Python version and give a warning if there is a mismatch:
        shell_commands += "py_version=`python -V | awk '{{print $2}}'`\n"
        shell_commands += f'if [[ "{fn_version}" != "$py_version" ]]; then\n'
        shell_commands += '  echo "Warning: Python version mismatch:"\n'
        shell_commands += f'  echo "Workflow version is {fn_version}. Conda environment version is $py_version."\n'
        shell_commands += "fi\n\n"

        shell_commands += "python - <<EOF\n"
        shell_commands += "import cloudpickle as pickle\n"
        shell_commands += "import os\n\n"

        # Add Python commands to run the pickled function:
        shell_commands += f'with open("{temp_filename}", "rb") as f:\n'
        shell_commands += "    fn = pickle.load(f)\n\n"

        shell_commands += f'os.remove("{temp_filename}")\n\n'

        shell_commands += f"result = fn(*{args}, **{kwargs})\n\n"

        shell_commands += f'with open("{result_filename}", "wb") as f:\n'
        shell_commands += "    pickle.dump(result, f)\n"
        shell_commands += "EOF\n"

        # Run the script and unpickle the result
        with tempfile.NamedTemporaryFile(dir=cache_dir, mode="w") as f:
            f.write(shell_commands)
            f.flush()

            out = subprocess.run(["bash", f.name], capture_output=True, encoding="utf-8")

            if len(out.stdout) != 0:
                # These are print/log statements from the task.
                print(out.stdout)

            if out.returncode != 0:
                app_log.warning(out.stderr)
                return self._on_conda_env_fail(fn, args, kwargs, node_id)

        with open(result_filename, "rb") as f:
            result = pickle.load(f)

            message = f"Executed node {node_id} on Conda environment {self.conda_env}."
            app_log.debug(message)
            return result

    def _on_conda_env_fail(self, fn: Callable, args: List, kwargs: Dict, node_id: int):
        """

        Args:
            fn: The input python function which will be executed and
                whose result may be returned by this function.
            args: List of positional arguments to be used by the function.
            kwargs: Dictionary of keyword arguments to be used by the function.
            node_id: The integer identifier for the current node.

        Returns:
            output: The result of the function execution, if
                self.current_env_on_conda_fail == True, otherwise, return value is None.
        """

        result = None
        message = f"Failed to execute node {node_id} on Conda environment {self.conda_env}."
        if self.current_env_on_conda_fail:
            message += "\nExecuting on the current Conda environment."
            app_log.warning(message)
            result = fn(*args, **kwargs)

        else:
            app_log.error(message)
            raise RuntimeError

        return result

    def get_conda_envs(self) -> None:
        """
        Print a list of Conda environments detected on the system.

        Args:
            None

        Returns:
            None
        """

        self.conda_envs = []

        env_output = subprocess.run(
            ["conda", "env", "list"], capture_output=True, encoding="utf-8"
        )

        if len(env_output.stderr) > 0:
            message = f"Problem in listing Conda environments:\n{env_output.stderr}"
            app_log.warning(message)
            return

        for line in env_output.stdout.split("\n"):
            if not line.startswith("#"):
                row = line.split()
                if len(row) > 1:
                    if "*" in row:
                        self.current_env = row[0]
                    self.conda_envs.append(row[0])

        app_log.debug(f"Conda environments:\n{self.conda_envs}")

    def get_conda_path(self) -> bool:
        """
        Query the path where the conda executable can be found.

        Args:
            None

        Returns:
            found: True if Conda is found on the system.
        """

        self.conda_path = ""
        which_conda = subprocess.run(
            ["which", "conda"], capture_output=True, encoding="utf-8"
        ).stdout
        if which_conda == "":
            message = "No Conda installation found on this compute node."
            app_log.warning(message)
            return False
        self.conda_path = which_conda
        return True
