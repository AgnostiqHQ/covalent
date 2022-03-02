from typing import Any, Optional

from app.schemas.workflow import DispatchResponse, UpdateWorkflowRequest, UpdateWorkFlowResponse
from fastapi import APIRouter, File

router = APIRouter()


@router.post("/{dispatch_id}/dispatch", status_code=200, response_model=DispatchResponse)
def submit_workflow(*, dispatch_id: str) -> Any:
    """
    Submit a workflow
    """
    return {"dispatch_id": "48f1d3b7-27bb-4c5d-97fe-c0c61c197fd5"}


@router.post("/{dispatch_id}/cancel", status_code=200, response_model=DispatchResponse)
def cancel_workflow(*, dispatch_id: str) -> Any:
    """
    Cancel a workflow
    """
    return {"dispatch_id": "48f1d3b7-27bb-4c5d-97fe-c0c61c197fd5"}


@router.put("/{dispatch_id}/update", status_code=200, response_model=UpdateWorkFlowResponse)
def update_workflow(*, body: UpdateWorkflowRequest) -> Any:
    """
    Update a workflow
    """
    return {
        "status": "COMPLETED",
        "result": {
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
        },
    }
