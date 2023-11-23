# Copyright 2023 Agnostiq Inc.
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

import asyncio
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from threading import Thread
from typing import Any, Dict, List, Optional, Sequence, Union

import orjson
import pennylane as qml
from mpire import WorkerPool
from pydantic import (  # pylint: disable=no-name-in-module
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from .._shared_files.qinfo import QElectronInfo, QNodeSpecs

__all__ = [
    "BaseQExecutor",
    "BaseProcessPoolQExecutor",
    "AsyncBaseQExecutor",
    "BaseThreadPoolQExecutor",
]

SHOTS_DEFAULT = -1


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()  # pylint: disable=no-member


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
    """
    Base class for all Quantum Executors.
    """

    shots: Union[None, int, Sequence[int], Sequence[Union[int, Sequence[int]]]] = SHOTS_DEFAULT
    shots_converter: Optional[type] = None
    persist_data: bool = True

    # Executors need to contain certain information about original QNode, in order
    # to produce correct results. These attributes below contain that information.
    # They are set inside the `QServer` and will be `None` client-side.
    qelectron_info: Optional[QElectronInfo] = None
    qnode_specs: Optional[QNodeSpecs] = None

    @property
    def override_shots(self) -> Union[int, None]:
        """
        Fallback to the QNode device's shots if no user-specified shots on executor.
        """

        if self.shots is SHOTS_DEFAULT:
            # No user-specified shots. Use the original QNode device's shots instead.
            shots = self.qelectron_info.device_shots
            shots_converter = self.qelectron_info.device_shots_type
            return shots_converter(shots) if shots_converter is not None else shots
        if self.shots is None:
            # User has specified `shots=None` on executor.
            return None

        if isinstance(self.shots, Sequence) and self.shots_converter is not None:
            return self.shots_converter(self.shots)

        # User has specified `shots` as an int.
        return self.shots

    model_config = ConfigDict(extra="allow")

    @model_validator(mode="before")
    @classmethod
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

    def run_circuit(self, qscript, device, result_obj: "QCResult") -> "QCResult":
        start_time = time.perf_counter()
        results = qml.execute([qscript], device, gradient_fn="best")
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time

        return result_obj

    def dict(self, *args, **kwargs):
        dict_ = super().model_dump(*args, **kwargs)

        # Ensure shots is a hashable value.
        shots = dict_.get("shots")
        if isinstance(shots, Sequence):
            dict_["shots"] = tuple(shots)

            # Set shots converter to recover original sequence type.
            shots_converter = dict_.get("shots_converter")
            if shots_converter is None:
                dict_["shots_converter"] = type(shots)

        return dict_


class QCResult(BaseModel):
    """
    Container for results from `run_circuit` methods. Standardizes output and allows
    metadata to be updated at various points.
    """

    results: Optional[Any] = None
    execution_time: float = None
    metadata: Dict[str, Any] = Field(default_factory=lambda: {"execution_metadata": []})

    def expand(self) -> List["QCResult"]:
        """
        Expand result object into a list of result objects, one for each execution.
        """
        result_objs = []
        for i, result in enumerate(self.results):
            # Copy other non-execution metadata.
            _result_obj = QCResult(
                results=[result], execution_time=self.execution_time, metadata={}
            )

            # Handle single and multi-component metadata.
            execution_metadata = self.metadata["execution_metadata"]
            if len(self.metadata["execution_metadata"]) > 0:
                execution_metadata = execution_metadata[i]

            # Populate corresponding metadata.
            _result_obj.metadata.update(
                execution_metadata=[execution_metadata],
                device_name=self.metadata["device_name"],
                executor_name=self.metadata["executor_name"],
                executor_backend_name=self.metadata["executor_backend_name"],
            )

            result_objs.append(_result_obj)

        return result_objs

    @classmethod
    def with_metadata(cls, *, device_name: str, executor: BaseQExecutor):
        """
        Create a blank instance with pre-set metadata.
        """
        result_obj = cls()
        backend_name = executor.backend if hasattr(executor, "backend") else ""
        result_obj.metadata.update(
            device_name=device_name,
            executor_name=executor.__class__.__name__,
            executor_backend_name=backend_name,
        )
        return result_obj


class SyncBaseQExecutor(BaseQExecutor):
    device: Optional[str] = "default.qubit"

    def run_all_circuits(self, qscripts_list) -> List[QCResult]:
        result_objs: List[QCResult] = []

        for qscript in qscripts_list:
            dev = qml.device(
                self.device,
                wires=self.qelectron_info.device_wires,
                shots=self.qelectron_info.device_shots,
            )

            result_obj = QCResult.with_metadata(device_name=dev.short_name, executor=self)
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

    device: Optional[str] = "default.qubit"

    def batch_submit(self, qscripts_list):
        futures = []
        loop = get_asyncio_event_loop()
        for qscript in qscripts_list:
            dev = qml.device(
                self.device,
                wires=self.qelectron_info.device_wires,
                shots=self.qelectron_info.device_shots,
            )

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
        results = qml.execute([qscript], device, gradient_fn="best")
        end_time = time.perf_counter()

        result_obj.results = results
        result_obj.execution_time = end_time - start_time

        return result_obj


class BaseProcessPoolQExecutor(BaseQExecutor):
    device: Optional[str] = "default.qubit"
    num_processes: int = 10

    def batch_submit(self, qscripts_list):
        pool = get_process_pool(self.num_processes)

        futures = []
        for qscript in qscripts_list:
            dev = qml.device(
                self.device,
                wires=self.qelectron_info.device_wires,
                shots=self.qelectron_info.device_shots,
            )

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
    device: Optional[str] = "default.qubit"
    num_threads: int = 10

    def batch_submit(self, qscripts_list):
        pool = get_thread_pool(self.num_threads)

        futures = []
        for qscript in qscripts_list:
            dev = qml.device(
                self.device,
                wires=self.qelectron_info.device_wires,
                shots=self.qelectron_info.device_shots,
            )

            result_obj = QCResult.with_metadata(
                device_name=dev.short_name,
                executor=self,
            )
            fut = pool.submit(self.run_circuit, qscript, dev, result_obj)
            futures.append(fut)

        return futures

    def batch_get_results(self, futures_list: List) -> List[QCResult]:
        return [fut.result() for fut in futures_list]
