from typing import Any, Optional, Sequence

from app.schemas.common import HTTPExceptionSchema
from app.schemas.workflow import Result
from fastapi import APIRouter, File

router = APIRouter()

mock_result_object_instance = {
    "dispatch_id": "",
    "results_dir": "",
    "status": "COMPLETED",
    "graph": {
        "links": [{"edge_name": "data", "param_type": "kwarg", "source": 0, "target": 1}],
        "nodes": [
            {
                "name": "load_data",
                "metadata": {"executor": "<LocalExecutor>"},
                "function_string": "@ct.electron\ndef load_data():\n    iris = datasets.load_iris()\n    perm = permutation(iris.target.size)\n    iris.data = iris.data[perm]\n    iris.target = iris.target[perm]\n    return iris.data, iris.target\n\n\n",
                "start_time": "2022-02-28T23:21:17.844268+00:00",
                "end_time": "2022-02-28T23:21:17.853741+00:00",
                "status": "COMPLETED",
                "output": ["[[5.  3.4 1.5 0.2]]"],
                "error": None,
                "sublattice_result": None,
                "stdout": "",
                "stderr": "",
                "id": 0,
                "doc": None,
                "kwargs": None,
            }
        ],
    },
}


@router.get("/results", status_code=200, response_model=Sequence[Result])
def get_results() -> Any:
    """
    Get all results
    """
    return [mock_result_object_instance, mock_result_object_instance]


@router.get(
    "/results/{dispatch_id}",
    status_code=200,
    response_model=Result,
    responses={
        404: {"model": HTTPExceptionSchema, "description": "The result was not found"},
    },
)
def get_result(
    *,
    dispatch_id: str,
) -> Any:
    """
    Get a result object
    """
    return mock_result_object_instance


@router.post("/results", status_code=200)
def create_result(
    *,
    result_input: Result,
) -> Any:
    """
    Get a result object
    """
    return mock_result_object_instance
