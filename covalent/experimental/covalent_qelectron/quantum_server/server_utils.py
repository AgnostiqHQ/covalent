import datetime
import importlib
from functools import lru_cache
from typing import Any, Dict, List

import orjson
from pydantic import BaseModel

from ..executors import BaseQExecutor

BATCH_ID_SEPARATOR = "@"
MAX_DIFFERENT_EXECUTORS = 10


class CircuitInfo(BaseModel):
    electron_node_id: str = None
    dispatch_id: str = None
    circuit_name: str = None
    circuit_description: str = None
    qnode_specs: Dict[str, Any] = None
    qexecutor: BaseQExecutor = None
    save_time: datetime.datetime
    circuit_id: str = None
    qscript: str = None
    execution_time: float = None
    result: List[Any] = None
    result_metadata: List[Dict[str, Any]] = None


@lru_cache
def get_cached_module():
    return importlib.import_module(
        ".experimental.covalent_qelectron.quantum_server.proxy_executors",
        package="covalent"
    )


def executor_from_dict(executor_dict: Dict):

    if "executors" in executor_dict:
        executors = [executor_from_dict(ed) for ed in executor_dict["executors"]]
        executor_dict["executors"] = executors

    name = executor_dict["name"]
    executor_class = getattr(get_cached_module(), name)
    return executor_class(**executor_dict)


@lru_cache(maxsize=MAX_DIFFERENT_EXECUTORS)
def get_cached_executor(**executor_dict):

    if "executors" in executor_dict:
        executors = tuple(orjson.loads(ex) for ex in executor_dict["executors"])
        executor_dict["executors"] = executors

    return executor_from_dict(executor_dict)


def reconstruct_executors(deconstructed_executors: List[Dict]):
    return [executor_from_dict(de) for de in deconstructed_executors]


def get_circuit_id(batch_id, circuit_number):
    return f"circuit_{circuit_number}{BATCH_ID_SEPARATOR}{batch_id}"
