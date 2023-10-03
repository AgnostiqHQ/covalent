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

import codecs
import json
from typing import Optional
from uuid import UUID

import cloudpickle as pickle
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

import covalent_dispatcher as dispatcher
from covalent._results_manager.result import Result
from covalent._shared_files import logger

from .._db.datastore import workflow_db
from .._db.load import _result_from
from .._db.models import Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()


@router.post("/submit")
async def submit(request: Request, disable_run: bool = False) -> UUID:
    """
    Function to accept the submit request of
    new dispatch and return the dispatch id
    back to the client.

    Args:
        disable_run: Whether to disable the execution of this lattice

    Returns:
        dispatch_id: The dispatch id in a json format
                     returned as a Fast API Response object
    """
    try:
        data = await request.json()
        data = json.dumps(data).encode("utf-8")

        return await dispatcher.run_dispatcher(data, disable_run)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to submit workflow: {e}",
        ) from e


@router.post("/redispatch")
async def redispatch(request: Request, is_pending: bool = False) -> str:
    """Endpoint to redispatch a workflow."""
    try:
        data = await request.json()
        dispatch_id = data["dispatch_id"]
        json_lattice = data["json_lattice"]
        electron_updates = data["electron_updates"]
        reuse_previous_results = data["reuse_previous_results"]
        app_log.debug(
            f"Unpacked redispatch request for {dispatch_id}. reuse_previous_results: {reuse_previous_results}, electron_updates: {electron_updates}"
        )
        return await dispatcher.run_redispatch(
            dispatch_id, json_lattice, electron_updates, reuse_previous_results, is_pending
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to redispatch workflow: {e}",
        ) from e


@router.post("/cancel")
async def cancel(request: Request) -> str:
    """
    Function to accept the cancel request of
    a dispatch.

    Args:
        None

    Returns:
        Fast API Response object confirming that the dispatch
        has been cancelled.
    """

    data = await request.json()

    dispatch_id = data["dispatch_id"]
    task_ids = data["task_ids"]

    await dispatcher.cancel_running_dispatch(dispatch_id, task_ids)
    if task_ids:
        return f"Cancelled tasks {task_ids} in dispatch {dispatch_id}."
    else:
        return f"Dispatch {dispatch_id} cancelled."


@router.get("/result/{dispatch_id}")
async def get_result(
    dispatch_id: str, wait: Optional[bool] = False, status_only: Optional[bool] = False
):
    with workflow_db.session() as session:
        lattice_record = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
        status = lattice_record.status if lattice_record else None
        if not lattice_record:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )
        if not wait or status in [
            str(Result.COMPLETED),
            str(Result.FAILED),
            str(Result.CANCELLED),
            str(Result.POSTPROCESSING_FAILED),
            str(Result.PENDING_POSTPROCESSING),
        ]:
            output = {
                "id": dispatch_id,
                "status": lattice_record.status,
            }
            if not status_only:
                output["result"] = codecs.encode(
                    pickle.dumps(_result_from(lattice_record)), "base64"
                ).decode()
            return output

        return JSONResponse(
            status_code=503,
            content={
                "message": "Result not ready to read yet. Please wait for a couple of seconds."
            },
            headers={"Retry-After": "2"},
        )
