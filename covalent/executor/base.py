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

import asyncio
import copy
import io
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, ContextManager, Dict, Iterable, List

import aiofiles

from .._shared_files import TaskRuntimeError, logger
from .._shared_files.context_managers import active_dispatch_info_manager
from .._shared_files.util_classes import DispatchInfo
from .utils.wrappers import wrapper_fn  # nopycln: import

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class _AbstractBaseExecutor(ABC):
    """
    Private parent class for BaseExecutor and AsyncBaseExecutor

    Attributes:
        log_stdout: The path to the file to be used for redirecting stdout.
        log_stderr: The path to the file to be used for redirecting stderr.
        cache_dir: The location used for cached files in the executor.
        time_limit: time limit for the task
        retries: Number of times to retry execution upon failure

    """

    SUPPORTS_MANAGED_EXECUTION = False

    def __init__(
        self,
        log_stdout: str = "",
        log_stderr: str = "",
        cache_dir: str = "",
        time_limit: int = -1,
        retries: int = 0,
        *args,
        **kwargs,
    ):
        self.log_stdout = log_stdout
        self.log_stderr = log_stderr
        self.cache_dir = cache_dir
        self.time_limit = time_limit
        self.retries = retries

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

    def short_name(self):
        module = self.__module__
        return self.__module__.split("/")[-1].split(".")[-1]

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        return {
            "type": str(self.__class__),
            "short_name": self.short_name(),
            "attributes": self.__dict__.copy(),
        }

    def from_dict(self, object_dict: dict) -> "BaseExecutor":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            self

        Instance attributes will be overwritten.
        """
        if object_dict:
            self.__dict__ = copy.deepcopy(object_dict["attributes"])
        return self

    @property
    def task_stdout(self):
        return self.__dict__.get("_task_stdout")

    @property
    def task_stderr(self):
        return self.__dict__.get("_task_stderr")


class BaseExecutor(_AbstractBaseExecutor):
    """
    Base executor class to be used for defining any executor
    plugin. Subclassing this class will allow you to define
    your own executor plugin which can be used in covalent.

    Attributes:
        log_stdout: The path to the file to be used for redirecting stdout.
        log_stderr: The path to the file to be used for redirecting stderr.
        cache_dir: The location used for cached files in the executor.
        time_limit: time limit for the task
        retries: Number of times to retry execution upon failure

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(*args, **kwargs)

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

    async def _execute(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            self.execute,
            function,
            args,
            kwargs,
            dispatch_id,
            results_dir,
            node_id,
        )

    def execute(
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

        This calls the executor-specific `run()` method.

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
        self._task_stdout = io.StringIO()
        self._task_stderr = io.StringIO()

        task_metadata = {
            "dispatch_id": dispatch_id,
            "node_id": node_id,
            "results_dir": results_dir,
        }

        self.setup(task_metadata=task_metadata)

        try:
            result = self.run(function, args, kwargs, task_metadata)
            exception_raised = False
        except TaskRuntimeError as err:
            app_log.error(f"TaskRuntimeError: {err}")
            exception_raised = True
            result = None

        finally:
            self.teardown(task_metadata=task_metadata)

        self.write_streams_to_file(
            (self._task_stdout.getvalue(), self._task_stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (
            result,
            self._task_stdout.getvalue(),
            self._task_stderr.getvalue(),
            exception_raised,
        )

    def setup(self, task_metadata: Dict) -> Any:
        """Placeholder to run any executor specific tasks"""
        pass

    @abstractmethod
    def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict) -> Any:
        """Abstract method to run a function in the executor.

        Args:
            function: The function to run in the executor
            args: List of positional arguments to be used by the function
            kwargs: Dictionary of keyword arguments to be used by the function.
            task_metadata: Dictionary of metadata for the task. Current keys are
                          `dispatch_id` and `node_id`

        Returns:
            output: The result of the function execution
        """

        raise NotImplementedError

    def teardown(self, task_metadata: Dict) -> Any:
        """Placeholder to run nay executor specific cleanup/teardown actions"""
        pass

    async def send(
        self,
        task_specs: List[Dict],
        resources: dict,
        task_group_metadata: dict,
    ):
        # Task specs are of the form
        # {"function_ref": [node_id], "args_refs": [node_ids], "kwargs_refs": {key: node_id}}

        # Assets are assumed to be accessible by the compute backend
        # at the provided URIs

        # The Asset Manager is responsible for uploading all assets
        # Returns a job handle (should be JSONable)

        raise NotImplementedError

    async def poll(self, task_group_metadata: Dict, job_handle: Any):

        # To be run as a background task.  A callback will be
        # registered with the runner to invoke the receive()

        return -1

    async def receive(self, task_metadata: Dict, job_handle: Any):

        # Returns (output_uri, stdout_uri, stderr_uri,
        # exception_raised)

        # Job should have reached a terminal state by the time this is invoked.

        raise NotImplementedError

    def get_upload_uri(self, task_metadata: Dict, object_key: str):
        return ""


class AsyncBaseExecutor(_AbstractBaseExecutor):
    """Async base executor class to be used for defining any executor
    plugin. Subclassing this class will allow you to define
    your own executor plugin which can be used in covalent.

    This is analogous to `BaseExecutor` except the `run()` method,
    together with the optional `setup()` and `teardown()` methods, are
    coroutines.

    Attributes:
        log_stdout: The path to the file to be used for redirecting stdout.
        log_stderr: The path to the file to be used for redirecting stderr.
        cache_dir: The location used for cached files in the executor.
        time_limit: time limit for the task
        retries: Number of times to retry execution upon failure

    """

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:

        super().__init__(*args, **kwargs)

    async def write_streams_to_file(
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

        This uses aiofiles to avoid blocking the event loop.
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

                async with aiofiles.open(filepath, "a") as f:
                    await f.write(ss)

    async def _execute(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:

        return await self.execute(
            function,
            args,
            kwargs,
            dispatch_id,
            results_dir,
            node_id,
        )

    async def execute(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:

        self._task_stdout = io.StringIO()
        self._task_stderr = io.StringIO()

        task_metadata = {
            "dispatch_id": dispatch_id,
            "node_id": node_id,
            "results_dir": results_dir,
        }

        await self.setup(task_metadata=task_metadata)

        try:
            result = await self.run(function, args, kwargs, task_metadata)
            exception_raised = False
        except TaskRuntimeError as err:
            exception_raised = True
            result = None

        finally:
            await self.teardown(task_metadata=task_metadata)

        await self.write_streams_to_file(
            (self._task_stdout.getvalue(), self._task_stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (
            result,
            self._task_stdout.getvalue(),
            self._task_stderr.getvalue(),
            exception_raised,
        )

    async def setup(self, task_metadata: Dict):
        """Executor specific setup method"""
        pass

    async def teardown(self, task_metadata: Dict):
        """Executor specific teardown method"""
        pass

    @abstractmethod
    async def run(self, function: Callable, args: List, kwargs: Dict, task_metadata: Dict) -> Any:
        """Abstract method to run a function in the executor in async-aware manner.

        Args:
            function: The function to run in the executor
            args: List of positional arguments to be used by the function
            kwargs: Dictionary of keyword arguments to be used by the function.
            task_metadata: Dictionary of metadata for the task. Current keys are
                          `dispatch_id` and `node_id`

        Returns:
            output: The result of the function execution
        """

        raise NotImplementedError

    async def send(
        self,
        task_specs: List[Dict],
        resources: dict,
        task_group_metadata: dict,
    ):
        # Assets are assumed to be accessible by the compute backend
        # at the provided URIs

        # The Asset Manager is responsible for uploading all assets
        # Returns a job handle (should be JSONable)

        raise NotImplementedError

    async def poll(self, task_metadata: Dict, job_handle: Any):

        # To be run as a background task.  A callback will be
        # registered with the runner to invoke the receive()

        return -1

    async def receive(self, task_metadata: Dict, job_handle: Any):

        # Returns a list of task results
        # {
        #   "dispatch_id": dispatch_id,
        #   "node_id": node_id,
        #   "output_uri": output_uri,
        #   "stdout_uri": stdout_uri,
        #   "stderr_uri": stderr_uri,
        #   "status": status,
        # }

        # Job should have reached a terminal state by the time this is invoked.

        raise NotImplementedError

    def get_upload_uri(self, task_group_metadata: Dict, object_key: str):
        return ""
