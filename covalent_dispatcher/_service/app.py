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

import asyncio
import json
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import APIRouter, FastAPI, HTTPException, Request

import covalent_dispatcher as dispatcher
from covalent._shared_files import logger
from covalent_dispatcher._core import dispatcher as core_dispatcher
from covalent_dispatcher._core import runner_exp as core_runner

from .._db.dispatchdb import DispatchDB
from .heartbeat import Heartbeat

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

_futures = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize global variables"""

    heartbeat = Heartbeat()
    fut = asyncio.create_task(heartbeat.start())
    _futures.add(fut)
    fut.add_done_callback(_futures.discard)

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


@router.post("/submit")
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
        return await dispatcher.run_dispatcher(data)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to submit workflow: {e}",
        ) from e


@router.post("/redispatch")
async def redispatch(request: Request) -> str:
    """Endpoint to redispatch a workflow."""
    try:
        data = await request.json()
        dispatch_id = data["dispatch_id"]
        json_lattice = data["json_lattice"]
        electron_updates = data["electron_updates"]
        reuse_previous_results = data["reuse_previous_results"]
        return await dispatcher.run_redispatch(
            dispatch_id,
            json_lattice,
            electron_updates,
            reuse_previous_results,
        )

    except Exception as e:
        app_log.exception(f"Exception in redispatch handler: {e}")
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


@router.get("/db-path")
def db_path() -> str:
    db_path = DispatchDB()._dbpath
    return json.dumps(db_path)
