# Copyright 2023 Agnostiq Inc.
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

import asyncio
import time
from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from functools import lru_cache
from threading import Thread
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import orjson
import pennylane as qml
from mpire import WorkerPool
from mpire.async_result import AsyncResult
from pydantic import BaseModel, Extra, Field, root_validator  # pylint: disable=no-name-in-module

from covalent._shared_files.config import get_config

__all__ = [
    "BaseQExecutor",
    "BaseProcessPoolQExecutor",
    "AsyncBaseQExecutor",
    "BaseThreadPoolQExecutor",
    "AsyncBaseQCluster"
]


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


@lru_cache
def get_process_pool(num_processes=None):
    return WorkerPool(n_jobs=num_processes)


@lru_cache
def get_thread_pool(max_workers=None):
    return ThreadPoolExecutor(max_workers=max_workers)


@lru_cache
def get_asyncio_event_loop():
    """
    Returns an asyncio event loop running in a separate thread.
    """

    def _run_loop(_loop):
        asyncio.set_event_loop(_loop)
        _loop.run_forever()

    loop = asyncio.new_event_loop()
    thread = Thread(target=_run_loop, args=(loop,), daemon=True)
    thread.start()

    # Create function attribute so reference to thread is not lost.
    get_asyncio_event_loop.thread = thread

    return loop


class BaseQExecutor(ABC, BaseModel):

    persist_data: bool = Field(
        default_factory=lambda: get_config("qelectron")["persist_data"]
    )

    class Config:
        extra = Extra.allow

    @root_validator(pre=True)
    def set_name(cls, values):
        # pylint: disable=no-self-argument
        # Set the `name` attribute to the class name
        values["name"] = cls.__name__
        return values

    @abstractmethod
    def batch_submit(self, qscripts_list):
        raise NotImplementedError

    @abstractmethod
    def batch_get_results(self, futures_list):
        raise NotImplementedError

    def run_circuit(self, qscript, device, result_obj: 'QCResult') -> 'QCResult':
        start_time = time.perf_counter()
        results = qml.execute([qscript], device, None)
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time

        return result_obj

    # To make executor instances re-usable, these attributes are set
    # server-side, after reconstruction.
    qnode_device_import_path: Tuple[str, str] = None
    qnode_device_shots: Optional[int] = None
    qnode_device_wires: int = None
    pennylane_active_return: bool = None


class QCResult(BaseModel):
    """
    Container for results from `run_circuit` methods. Standardizes output and allows
    metadata to be updated at various points.
    """

    results: Optional[Any] = None
    execution_time: float = None
    metadata: Dict[str, Any] = Field(default_factory=lambda: {"execution_metadata": []})

    @classmethod
    def with_metadata(cls, *, device_name: str, executor: BaseQExecutor):
        """
        create an blank instance with pre-set metadata
        """
        result_obj = cls()
        backend_name = ""
        if hasattr(executor, "backend_name"):
            backend_name = executor.backend_name

        result_obj.metadata.update(
            device_name=device_name,
            executor_name=executor.__class__.__name__,
            executor_backend_name=backend_name,
        )
        return result_obj


class SyncBaseQExecutor(BaseQExecutor):

    device: str = Field(
        default_factory=lambda: get_config("qelectron")["device"]
    )

    def run_all_circuits(self, qscripts_list) -> List[QCResult]:

        result_objs: List[QCResult] = []

        for qscript in qscripts_list:
            dev = qml.device(self.device, wires=qscript.wires)

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self
            )
            result_obj = self.run_circuit(qscript, dev, result_obj)
            result_objs.append(result_obj)

        return result_objs

    def batch_submit(self, qscripts_list):
        # Offload execution of all circuits to the same thread
        # so that the qserver isn't blocked by their completion.
        pool = get_thread_pool()
        fut = pool.submit(self.run_all_circuits, qscripts_list)
        dummy_futures = [fut] * len(qscripts_list)
        return dummy_futures

    def batch_get_results(self, futures_list):
        return futures_list[0].result()


class AsyncBaseQExecutor(BaseQExecutor):
    """
    Executor that uses `asyncio` to handle multiple job submissions
    """

    # pylint: disable=invalid-overridden-method

    device: str = Field(
        default_factory=lambda: get_config("qelectron")["device"]
    )

    def batch_submit(self, qscripts_list):

        futures = []
        loop = get_asyncio_event_loop()
        for qscript in qscripts_list:
            dev = qml.device(self.device, wires=qscript.wires)

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )
            fut = loop.create_task(self.run_circuit(qscript, dev, result_obj))
            futures.append(fut)

        return futures

    def batch_get_results(self, futures_list: List):

        loop = get_asyncio_event_loop()
        task = asyncio.run_coroutine_threadsafe(self._get_result(futures_list), loop)
        return task.result()

    async def _get_result(self, futures_list: List) -> List[QCResult]:
        return await asyncio.gather(*futures_list)

    async def run_circuit(self, qscript, device, result_obj) -> QCResult:
        await asyncio.sleep(0)
        start_time = time.perf_counter()
        results = qml.execute([qscript], device, None)
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time

        return result_obj


class BaseProcessPoolQExecutor(BaseQExecutor):

    device: str = Field(
        default_factory=lambda: get_config("qelectron")["device"]
    )
    num_processes: int = Field(
        default_factory=lambda: get_config("qelectron")["num_processes"]
    )

    def batch_submit(self, qscripts_list):
        pool = get_process_pool(self.num_processes)

        futures = []
        for qscript in qscripts_list:
            dev = qml.device(self.device, wires=qscript.wires)

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )
            fut = pool.apply_async(self.run_circuit, args=(qscript, dev, result_obj))
            futures.append(fut)

        return futures

    def batch_get_results(self, futures_list: List) -> List[QCResult]:
        return [fut.get() for fut in futures_list]


class BaseThreadPoolQExecutor(BaseQExecutor):

    device: str = Field(
        default_factory=lambda: get_config("qelectron")["device"]
    )
    num_threads: int = Field(
        default_factory=lambda: get_config("qelectron")["num_threads"]
    )

    def batch_submit(self, qscripts_list):
        pool = get_thread_pool(self.num_threads)

        futures = []
        for qscript in qscripts_list:
            dev = qml.device(self.device, wires=qscript.wires)

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )
            fut = pool.submit(self.run_circuit, qscript, dev, result_obj)
            futures.append(fut)

        return futures

    def batch_get_results(self, futures_list: List) -> List[QCResult]:
        return [fut.result() for fut in futures_list]


class AsyncBaseQCluster(AsyncBaseQExecutor):

    executors: Tuple[BaseQExecutor, ...]
    selector: Union[str, Callable]

    _selector_serialized: bool = False

    @abstractmethod
    def serialize_selector(self) -> None:
        """
        Serializes the cluster's selector function.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize_selector(self) -> Union[str, Callable]:
        """
        Deserializes the cluster's selector function.
        """
        raise NotImplementedError

    @abstractmethod
    def dict(self, *args, **kwargs) -> dict:
        """
        Custom dict method to create a hashable `executors` attribute.
        """
        raise NotImplementedError

    @abstractmethod
    def get_selector(self):
        """
        Returns the deserialized selector function.
        """
        raise NotImplementedError

    async def _get_result(self, futures_list: List) -> List[QCResult]:
        """
        Override the base method to handle the case where the `futures_list`
        contains a mix of object types from various executors.
        """
        results_and_times = []
        for fut in futures_list:
            if isinstance(fut, asyncio.Task):
                results_and_times.append(await fut)
            elif isinstance(fut, Future):
                results_and_times.append(fut.result())
            elif isinstance(fut, AsyncResult):
                results_and_times.append(fut.get())
            else:
                results_and_times.append(fut)

        return results_and_times


class BaseQSelector(ABC, BaseModel):

    name: str = "base_qselector"

    def __call__(self, qscript, executors):
        """"
        Interface used by the quantum server.
        """
        return self.selector_function(qscript, executors)

    @abstractmethod
    def selector_function(self, qscript, executors):
        """
        Implement selection logic here.
        """
        raise NotImplementedError

    class Config:
        # Allows defining extra state fields in subclasses.
        extra = Extra.allow
