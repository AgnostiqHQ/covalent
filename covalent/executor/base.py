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
import threading
import uuid
from abc import ABC, abstractmethod
from contextlib import redirect_stderr, redirect_stdout
from functools import partial
from pathlib import Path
from typing import Any, Callable, ContextManager, Dict, Iterable, List, Tuple

import aiofiles

from covalent._workflow.depscall import RESERVED_RETVAL_KEY__FILES
from covalent.executor._runtime.utils import ExecutorCache

from .._shared_files import logger
from .._shared_files.context_managers import active_dispatch_info_manager
from .._shared_files.util_classes import DispatchInfo
from .._workflow.transport import TransportableObject

app_log = logger.app_log
log_stack_info = logger.log_stack_info


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

    cb_retvals = {}
    for tup in call_before:
        serialized_fn, serialized_args, serialized_kwargs, retval_key = tup
        cb_fn = serialized_fn.get_deserialized()
        cb_args = serialized_args.get_deserialized()
        cb_kwargs = serialized_kwargs.get_deserialized()
        retval = cb_fn(*cb_args, **cb_kwargs)

        # we always store cb_kwargs dict values as arrays to factor in non-unique values
        if retval_key and retval_key in cb_retvals:
            cb_retvals[retval_key].append(retval)
        elif retval_key:
            cb_retvals[retval_key] = [retval]

    # if cb_retvals key only contains one item this means it is a unique (non-repeated) retval key
    # so we only return the first element however if it is a 'files' kwarg we always return as a list
    cb_retvals = {
        key: value[0] if len(value) == 1 and key != RESERVED_RETVAL_KEY__FILES else value
        for key, value in cb_retvals.items()
    }

    fn = function.get_deserialized()

    new_args = [arg.get_deserialized() for arg in args]

    new_kwargs = {k: v.get_deserialized() for k, v in kwargs.items()}

    # Inject return values into kwargs
    for key, val in cb_retvals.items():
        new_kwargs[key] = val

    output = fn(*new_args, **new_kwargs)

    for tup in call_after:
        serialized_fn, serialized_args, serialized_kwargs, retval_key = tup
        ca_fn = serialized_fn.get_deserialized()
        ca_args = serialized_args.get_deserialized()
        ca_kwargs = serialized_kwargs.get_deserialized()
        ca_fn(*ca_args, **ca_kwargs)

    return TransportableObject(output)


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

        self.instance_id = int(uuid.uuid4())
        self.shared = False

    def clone(self):
        new_exec = copy.deepcopy(self)
        new_exec.instance_id = int(uuid.uuid4())
        return new_exec

    def get_shared_instance(self) -> "_AbstractBaseExecutor":
        shared_exec = self.clone()
        shared_exec.shared = True
        return shared_exec

    def is_shared_instance(self) -> bool:
        return self.shared

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
            "attributes": copy.deepcopy(self.__dict__),
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

        # Runtime state: must not be persisted

        # internals
        self._task_lock = None
        self._resource_lock = None
        self._warmed_up = False
        self._tasks_left = 1

        # task and resource state
        self._state = {}

    def _initialize_runtime(self, executor_cache: ExecutorCache = None):
        self._task_lock = threading.Lock()
        self._resource_lock = threading.Lock()
        if executor_cache:
            self._tasks_left = executor_cache.tasks_per_instance[self.instance_id]

            executor_cache.id_instance_map[self.instance_id] = self

        self._state["tasks"] = {}
        self._state["resource_metadata"] = {}

    def _set_resource_metadata(self, metadata):
        self._state["resource_metadata"] = metadata

    def _get_resource_metadata(self):
        return self._state["resource_metadata"]

    def _decrement_task_count(self):
        with self._task_lock:
            self._tasks_left -= 1

    def _increment_task_count(self):
        with self._task_lock:
            self._tasks_left += 1

    def _initialize_task_data(self, dispatch_id: str, node_id: int):
        if dispatch_id not in self._state["tasks"]:
            self._state["tasks"][dispatch_id] = {}

        self._state["tasks"][dispatch_id][node_id] = {"_status": "RUNNING"}

    def _set_task_data(self, dispatch_id: str, node_id: int, key: str, val: Any):
        self._state["tasks"][dispatch_id][node_id][key] = val

    def _get_task_data(self, dispatch_id: str, node_id: int, key: str):
        return self._state["tasks"][dispatch_id][node_id][key]

    def _set_task_status(self, dispatch_id: str, node_id: int, status: str):
        self._set_task_data(dispatch_id, node_id, "_status", status)

    def _get_task_status(self, dispatch_id: str, node_id: int):
        return self._get_task_data(dispatch_id, node_id, "_status")

    def _get_registered_tasks(self):
        return self._state["tasks"]

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

    def cancel(self, dispatch_id: str, node_id: int):
        app_log.warning(f"Cancel not implemented for {type(self)}")

    def setup(self, task_metadata: Dict = {}):
        pass

    def teardown(self, resource_metadata: Dict = {}):
        # Relinquish all resources if called without task_metadata
        pass

    def _cancel_task(self, dispatch_id: str, node_id: int):
        with self._task_lock:
            status = self._get_task_status(dispatch_id, node_id)
            if status == "RUNNING":
                self._set_task_status(dispatch_id, node_id, "CANCELLING")

        if status == "RUNNING":
            self.cancel(dispatch_id, node_id)

    def _finalize_sync(self):

        # Because tasks are registered in _run_task's thread during
        # _execute_async(), any task that entered _run_task before
        # _finalize is called will be tracked.
        tasks = self._get_registered_tasks()

        # Don't use the default threadpool since it might be saturated
        # with running tasks
        cancel_threads = []
        for dispatch_id in tasks:
            for node_id in tasks[dispatch_id]:
                t = threading.Thread(target=self._cancel_task, args=[dispatch_id, node_id])
                t.start()
                cancel_threads.append(t)

        for t in cancel_threads:
            t.join()

        with self._resource_lock:
            resource_metadata = self._get_resource_metadata()
        self.teardown(resource_metadata)

    # To be invoked from the dispatcher's thread
    async def _finalize(self):
        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(None, self._finalize_sync)
        await fut

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

        task_metadata = {
            "dispatch_id": dispatch_id,
            "node_id": node_id,
            "results_dir": results_dir,
        }

        with self._task_lock:
            self._initialize_task_data(dispatch_id, node_id)

        # Use a dedicated lock b/c this might block for a long time
        with self._resource_lock:
            if not self._warmed_up:
                resource_metadata = self.setup(task_metadata=task_metadata)
                self._set_resource_metadata(resource_metadata)
                self._warmed_up = True

        dispatch_info = DispatchInfo(dispatch_id)
        fn_version = function.args[0].python_version

        try:
            with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(
                io.StringIO()
            ) as stderr:
                result = self.run(function, args, kwargs, task_metadata)

            with self._task_lock:
                self._set_task_status(dispatch_id, node_id, "COMPLETED")
        except Exception as ex:
            with self._task_lock:
                # Check if we got here by cancellation
                if self._get_task_status(dispatch_id, node_id) == "CANCELLING":
                    self._set_task_status(dispatch_id, node_id, "CANCELLED")
                else:
                    self._set_task_status(dispatch_id, node_id, "FAILED")
            raise ex
        finally:
            self._decrement_task_count()
            if self._tasks_left < 1:
                with self._resource_lock:
                    resource_metadata = self._get_resource_metadata()
                self.teardown(resource_metadata)

        self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, stdout.getvalue(), stderr.getvalue())

    async def _execute_async(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:

        execute_callable = partial(
            self.execute,
            function=function,
            args=args,
            kwargs=kwargs,
            dispatch_id=dispatch_id,
            results_dir=results_dir,
            node_id=node_id,
        )

        self._initialize_task_data(dispatch_id, node_id)

        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(None, execute_callable)
        return await fut

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

        # Runtime state: must not be persisted

        # internals
        self._resource_lock = None
        self._warmed_up = False
        self._tasks_left = 1

        # User-defined state
        self._state = {}

    def _initialize_runtime(self, executor_cache: ExecutorCache = None):
        self._resource_lock = asyncio.Lock()
        if executor_cache:
            self._tasks_left = executor_cache.tasks_per_instance[self.instance_id]

            # Cache the executor if it is "shared"
            if self.shared:
                executor_cache.id_instance_map[self.instance_id] = self

        self._state["tasks"] = {}
        self._state["resource_metadata"] = {}

    def _set_resource_metadata(self, metadata):
        self._state["resource_metadata"] = metadata

    def _get_resource_metadata(self):
        return self._state["resource_metadata"]

    def _decrement_task_count(self):
        self._tasks_left -= 1

    def _increment_task_count(self):

        self._tasks_left += 1

    def _initialize_task_data(self, dispatch_id: str, node_id: int):
        if dispatch_id not in self._state["tasks"]:
            self._state["tasks"][dispatch_id] = {}

        self._state["tasks"][dispatch_id][node_id] = {"_status": "RUNNING"}

    def _set_task_data(self, dispatch_id: str, node_id: int, key: str, val: Any):
        self._state["tasks"][dispatch_id][node_id][key] = val

    def _get_task_data(self, dispatch_id: str, node_id: int, key: str):
        return self._state["tasks"][dispatch_id][node_id][key]

    def _set_task_status(self, dispatch_id: str, node_id: int, status: str):
        self._set_task_data(dispatch_id, node_id, "_status", status)

    def _get_task_status(self, dispatch_id: str, node_id: int):
        return self._get_task_data(dispatch_id, node_id, "_status")

    def _get_registered_tasks(self):
        return self._state["tasks"]

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

    async def cancel(self, dispatch_id: str, node_id: int):
        app_log.warning(f"Cancel not implemented for {type(self)}")

    async def setup(self, task_metadata: Dict = {}):
        pass

    async def teardown(self, resource_metadata: Dict = {}):
        # Relinquish all resources if called without task_metadata
        pass

    async def _cancel_task(self, dispatch_id: str, node_id: int):
        status = self._get_task_status(dispatch_id, node_id)
        if status == "RUNNING":
            self._set_task_status(dispatch_id, node_id, "CANCELLING")
            await self.cancel(dispatch_id, node_id)

    async def _finalize(self):
        tasks = self._get_registered_tasks()
        cancel_futures = []
        for dispatch_id in tasks:
            for node_id in tasks[dispatch_id]:
                fut = asyncio.create_task(self._cancel_task(dispatch_id, node_id))
                cancel_futures.append(fut)
        await asyncio.gather(*cancel_futures)

        await self.teardown(self._get_resource_metadata())

    async def execute(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:

        task_metadata = {
            "dispatch_id": dispatch_id,
            "node_id": node_id,
            "results_dir": results_dir,
        }
        async with self._resource_lock:
            if not self._warmed_up:
                resource_metadata = await self.setup(task_metadata=task_metadata)
                self._set_resource_metadata(resource_metadata)
                self._warmed_up = True

        try:
            with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(
                io.StringIO()
            ) as stderr:
                result = await self.run(function, args, kwargs, task_metadata)

            self._set_task_status(dispatch_id, node_id, "COMPLETED")
        except Exception as ex:
            # Check if we got here by cancellation
            if self._get_task_status(dispatch_id, node_id) == "CANCELLING":
                self._set_task_status(dispatch_id, node_id, "CANCELLED")
            else:
                self._set_task_status(dispatch_id, node_id, "FAILED")
            raise ex
        finally:
            self._decrement_task_count()
            if self._tasks_left < 1:
                resource_metadata = self._get_resource_metadata()

                # TODO: exceptions raised here should probably be handled
                # separately without changing the task outcome
                await self.teardown(resource_metadata)

        await self.write_streams_to_file(
            (stdout.getvalue(), stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, stdout.getvalue(), stderr.getvalue())

    async def _execute_async(
        self,
        function: Callable,
        args: List,
        kwargs: Dict,
        dispatch_id: str,
        results_dir: str,
        node_id: int = -1,
    ) -> Any:

        self._initialize_task_data(dispatch_id, node_id)

        return await self.execute(
            function=function,
            args=args,
            kwargs=kwargs,
            dispatch_id=dispatch_id,
            results_dir=results_dir,
            node_id=node_id,
        )

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
