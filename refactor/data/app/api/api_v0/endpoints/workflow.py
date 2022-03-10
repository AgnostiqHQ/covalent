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


from typing import Any, Union

from app.schemas.common import HTTPExceptionSchema
from app.schemas.workflow import (
    InsertResultResponse,
    Node,
    Result,
    ResultPickle,
    UpdateResultResponse,
)
from fastapi import APIRouter

router = APIRouter()

# For now we don't return this, instead just a bytes-like pickle object
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


@router.get(
    "/results/{dispatch_id}",
    status_code=200,
    response_model=ResultPickle,
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

    return {"result_object": b"result pickle object"}


@router.post("/results", status_code=200, response_model=InsertResultResponse)
def insert_result(
    *,
    result_object: Union[Result, ResultPickle],
) -> Any:
    """
    Insert a result object
    """

    return {"response": "Result successfully added to db"}


@router.put("/results/{dispatch_id}", status_code=200, response_model=UpdateResultResponse)
def update_result(
    *,
    dispatch_id: str,
    task: Node,
) -> Any:
    """
    Update a result object
    """

    return {"response": "Task updated successfully"}
