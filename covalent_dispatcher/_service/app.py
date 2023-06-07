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


"""Endpoints for dispatch management"""

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

import covalent_dispatcher.entry_point as dispatcher
from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.schemas.result import ResultSchema
from covalent_dispatcher._core import dispatcher as core_dispatcher
from covalent_dispatcher._core import runner_ng as core_runner

from .._dal.export import export_result_manifest
from .._db.datastore import workflow_db
from .._db.dispatchdb import DispatchDB
from .._db.models import Lattice
from .heartbeat import Heartbeat
from .models import ExportResponseSchema

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

_background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize global variables"""

    heartbeat = Heartbeat()
    fut = asyncio.create_task(heartbeat.start())
    _background_tasks.add(fut)
    fut.add_done_callback(_background_tasks.discard)

    # Runner event queue and listener
    core_runner._job_events = asyncio.Queue()
    core_runner._job_event_listener = asyncio.create_task(core_runner._listen_for_job_events())

    # Dispatcher event queue and listener
    core_dispatcher._global_status_queue = asyncio.Queue()
    core_dispatcher._global_event_listener = asyncio.create_task(
        core_dispatcher._node_event_listener()
    )

    yield

    core_dispatcher._global_event_listener.cancel()
    core_runner._job_event_listener.cancel()


@router.post("/dispatch/submit")
async def submit(request: Request) -> UUID:
    """
    Function to accept the submit request of
    new dispatch and return the dispatch id
    back to the client.

    Args:
        None

    Returns:
        dispatch_id: The dispatch id in a json format
                     returned as a Fast API Response object.
    """
    try:
        data = await request.json()
        data = json.dumps(data).encode("utf-8")
        return await dispatcher.make_dispatch(data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to submit workflow: {e}",
        ) from e


@router.post("/dispatch/cancel")
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


@router.get("/db-path")
def db_path() -> str:
    db_path = DispatchDB()._dbpath
    return json.dumps(db_path)


@router.post("/dispatch/register")
async def register(
    manifest: ResultSchema, parent_dispatch_id: Union[str, None] = None
) -> ResultSchema:
    try:
        return await dispatcher.register_dispatch(manifest, parent_dispatch_id)
    except Exception as e:
        app_log.debug(f"Exception in register: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to submit workflow: {e}",
        ) from e


@router.post("/dispatch/register/{dispatch_id}")
async def register_redispatch(
    manifest: ResultSchema,
    dispatch_id: str,
    reuse_previous_results: bool = False,
):
    try:
        return await dispatcher.register_redispatch(
            manifest,
            dispatch_id,
            reuse_previous_results,
        )
    except Exception as e:
        app_log.debug(f"Exception in register_redispatch: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to submit workflow: {e}",
        ) from e


@router.put("/dispatch/start/{dispatch_id}")
async def start(dispatch_id: str):
    try:
        fut = asyncio.create_task(dispatcher.start_dispatch(dispatch_id))
        _background_tasks.add(fut)
        fut.add_done_callback(_background_tasks.discard)

        return dispatch_id
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to start workflow: {e}",
        ) from e


@router.get("/dispatch/export/{dispatch_id}")
async def export_result(
    dispatch_id: str, wait: Optional[bool] = False, status_only: Optional[bool] = False
) -> ExportResponseSchema:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _export_result_sync,
        dispatch_id,
        wait,
        status_only,
    )


def _export_result_sync(
    dispatch_id: str, wait: Optional[bool] = False, status_only: Optional[bool] = False
) -> ExportResponseSchema:
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
                output["result_export"] = export_result_manifest(dispatch_id)

            return output

        response = JSONResponse(
            status_code=503,
            content={
                "message": "Result not ready to read yet. Please wait for a couple of seconds."
            },
            headers={"Retry-After": "2"},
        )
        return response
