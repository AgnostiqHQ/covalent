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


class BaseAsyncExecutor(ABC):
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

    @abstractmethod
    async def execute(
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
