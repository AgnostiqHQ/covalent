# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Class that defines the base executor template.
"""

import asyncio
import copy
import io
import json
import os
import queue
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import (
    Any,
    Callable,
    ContextManager,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import aiofiles

from covalent._shared_files.exceptions import TaskCancelledError
from covalent._workflow.depscall import RESERVED_RETVAL_KEY__FILES
from covalent.executor.utils import Signals

from .._shared_files import TaskRuntimeError, logger
from .._shared_files.context_managers import active_dispatch_info_manager
from .._shared_files.qelectron_utils import remove_qelectron_db
from .._shared_files.util_classes import RESULT_STATUS, DispatchInfo
from .._workflow.transport import TransportableObject

app_log = logger.app_log
log_stack_info = logger.log_stack_info
TypeJSON = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


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

    def _init_runtime(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cancel_pool: Optional[ThreadPoolExecutor] = None,
    ) -> None:
        """
        Create the required queues for cancel task messages to be shared back and forth

        Arg(s)
            loop: Asyncio event loop to create tasks on
            cancel_pool: A ThreadPoolExecutor object to submit tasks to

        Return(s)
            None
        """
        self._send_queue = asyncio.Queue()
        self._recv_queue = queue.Queue()
        self._loop = loop
        self._cancel_pool = cancel_pool

    def _notify(self, action: Signals, body: Any = None) -> None:
        """
        Notifies a waiting thread with the necessary action to take along with the arguments passed in as body

        Arg(s)
            action: One of three possible actions that a waiting thread must take -> Signals.GET, Signals.PUT, Signals.EXIT
            body: Respective arguments for each action

        Return(s)
            None
        """
        self._loop.call_soon_threadsafe(self._send_queue.put_nowait, (action, body))

    def _notify_sync(self, action: Signals, body: Any = None) -> Any:
        """
        Blocking version of the _notify method

        Arg(s)
            action: One of three possible actions that a waiting thread must take -> Signals.GET, Signals.PUT, Signals.EXIT
            body: Respective arguments for each action
        """
        self._notify(action, body)
        return self._wait_for_response()

    def _wait_for_response(self, timeout: int = 5) -> Any:
        """
        Wait for response from a thread depending on the action/body parameters sent

        Arg(s):
            timeout: Number of seconds to wait for the result to become available in the queue. Defaults to five seconds

        Return(s)
            body: Response to the corresponding action
        """
        status, body = self._recv_queue.get(timeout=timeout)
        if status is None:
            raise RuntimeError("Error waiting for response")
        return body

    def get_cancel_requested(self) -> bool:
        """
        Check if the task was requested to be cancelled by the user

        Arg(s)
            None

        Return(s)
            True/False whether task cancellation was requested
        """
        return self._notify_sync(Signals.GET, "cancel_requested")

    def set_job_handle(self, handle: TypeJSON) -> Any:
        """
        Save the job_id/handle returned by the backend executing the task

        Arg(s)
            handle: Any JSONable type to identifying the task being executed by the backend

        Return(s)
            Response from saving the job handle to database
        """
        return self._notify_sync(Signals.PUT, ("job_handle", json.dumps(handle)))

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
                    f.write(remove_qelectron_db(ss))

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

        try:
            self.setup(task_metadata=task_metadata)
            result = self.run(function, args, kwargs, task_metadata)
            job_status = RESULT_STATUS.COMPLETED
        except TaskRuntimeError as err:
            job_status = RESULT_STATUS.FAILED
            result = None
        except TaskCancelledError as err:
            job_status = RESULT_STATUS.CANCELLED
            result = None
        finally:
            self._notify(Signals.EXIT)
            self.teardown(task_metadata=task_metadata)

        self.write_streams_to_file(
            (self._task_stdout.getvalue(), self._task_stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, self._task_stdout.getvalue(), self._task_stderr.getvalue(), job_status)

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

    def cancel(self, task_metadata: Dict, job_handle: Any) -> Literal[False]:
        """
        Method to cancel the job identified uniquely by the `job_handle` (base class)

        Arg(s)
            task_metadata: Metadata of the task to be cancelled
            job_handle: Unique ID of the job assigned by the backend

        Return(s)
            False by default
        """
        app_log.debug(f"Cancel not implemented for executor {type(self)}")
        return False

    async def _cancel(self, task_metadata: Dict, job_handle: Any) -> Any:
        """
        Cancel the task in a non-blocking manner

        Arg(s)
            task_metadata: Metadata of the task to be cancelled
            job_handle: Unique ID of the job assigned by the backend

        Return(s)
           Result of the task cancellation
        """
        cancel_result = await self._loop.run_in_executor(
            self._cancel_pool, self.cancel, task_metadata, job_handle
        )
        await self._loop.run_in_executor(self._cancel_pool, self.teardown, task_metadata)
        return cancel_result

    def teardown(self, task_metadata: Dict) -> Any:
        """Placeholder to run any executor specific cleanup/teardown actions"""
        pass


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

    def _init_runtime(
        self,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        cancel_pool: Optional[ThreadPoolExecutor] = None,
    ) -> None:
        """
        Initialize the send and receive queues for communication between dispatcher and the executor

        Arg(s)
            loop: Asyncio event loop
            cancel_pool: Instance of a threadpool executor class

        Return(s)
            None
        """
        self._send_queue = asyncio.Queue()
        self._recv_queue = asyncio.Queue()

    def _notify(self, action: Signals, body: Any = None) -> None:
        """
        Notify the listener with the corresponding signal (async)

        Arg(s)
            action: Signal to the listener to trigger the corresponding action
            body: Message to be sent to the listener

        Return(s)
            None
        """
        self._send_queue.put_nowait((action, body))

    async def _notify_sync(self, action: Signals, body: Any = None) -> Any:
        """
        Blocking call to the `_notify` method to wait for response

        Arg(s)
            action: Signal to the listener to trigger the corresponding action
            body: Message to be sent to the listener

        Return(s)
            Response from the listener
        """
        self._notify(action, body)
        return await self._wait_for_response()

    async def _wait_for_response(self, timeout: int = 5) -> Any:
        """
        Block the thread until a response is recevied

        Arg(s)
            timeout: Number of seconds to wait until timing out

        Return(s)
            Response from the listener
        """
        aw = self._recv_queue.get()
        status, body = await asyncio.wait_for(aw, timeout=timeout)
        if status is False:
            raise RuntimeError("Error waiting for response")
        return body

    async def get_cancel_requested(self) -> Any:
        """
        Get if the task was requested to be canceled

        Arg(s)
            None

        Return(s)
            Whether the task has been requested to be cancelled
        """
        return await self._notify_sync(Signals.GET, "cancel_requested")

    async def set_job_handle(self, handle: TypeJSON) -> Any:
        """
        Save the job handle to database

        Arg(s)
            handle: JSONable type identifying the job being executed by the backend

        Return(s)
            Response from the listener that handles inserting the job handle to database
        """
        return await self._notify_sync(Signals.PUT, ("job_handle", json.dumps(handle)))

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
                    await f.write(remove_qelectron_db(ss))

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

        try:
            await self.setup(task_metadata=task_metadata)
            result = await self.run(function, args, kwargs, task_metadata)
            job_status = RESULT_STATUS.COMPLETED
        except TaskCancelledError as err:
            job_status = RESULT_STATUS.CANCELLED
            result = None
        except TaskRuntimeError as err:
            job_status = RESULT_STATUS.FAILED
            result = None
        finally:
            self._notify(Signals.EXIT)
            await self.teardown(task_metadata=task_metadata)

        await self.write_streams_to_file(
            (self._task_stdout.getvalue(), self._task_stderr.getvalue()),
            (self.log_stdout, self.log_stderr),
            dispatch_id,
            results_dir,
        )

        return (result, self._task_stdout.getvalue(), self._task_stderr.getvalue(), job_status)

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

    async def cancel(self, task_metadata: Dict, job_handle: Any) -> Literal[False]:
        """
        Executor specific task cancellation method

        Arg(s)
            task_metadata: Metadata associated with the task to be cancelled
            job_handle: Unique ID assigned to the job by the backend

        Return(s)
            False by default
        """
        app_log.debug(f"Cancel not implemented for executor {type(self)}")
        return False

    async def _cancel(self, task_metadata: Dict, job_handle: Any) -> Literal[False]:
        """
        Cancel the task in a non-blocking manner and teardown the infrastructure

        Arg(s)
            task_metadata: Metadata associated with the task to be cancelled
            job_handle: Unique ID assigned to the job by the backend

        Return(s)
            Result from cancelling the task
        """
        cancel_result = await self.cancel(task_metadata, job_handle)
        await self.teardown(task_metadata)
        return cancel_result
