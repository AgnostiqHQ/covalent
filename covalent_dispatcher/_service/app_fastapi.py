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

import codecs
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional
from uuid import UUID

import cloudpickle as pickle
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

import covalent_dispatcher as dispatcher
from covalent._data_store.models import Lattice
from covalent._results_manager.result import Result
from covalent._results_manager.results_manager import result_from

from .._db.dispatchdb import DispatchDB

router: APIRouter = APIRouter()


@router.on_event("startup")
def start_pools():
    global workflow_pool
    global tasks_pool

    workflow_pool = ThreadPoolExecutor()
    tasks_pool = ThreadPoolExecutor()


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
                     returned as a Flask Response object.
    """
    data = await request.json()
    data = json.dumps(data).encode("utf-8")

    dispatch_id = dispatcher.run_dispatcher(data, workflow_pool, tasks_pool)
    return dispatch_id


@router.post("/cancel")
def cancel(data: Any) -> str:
    """
    Function to accept the cancel request of
    a dispatch.

    Args:
        None

    Returns:
        Flask Response object confirming that the dispatch
        has been cancelled.
    """
    dispatcher.cancel_running_dispatch(data)
    return f"Dispatch {data} cancelled."


@router.get("/db-path")
def db_path() -> str:
    db_path = DispatchDB()._dbpath
    db_path = json.dumps(db_path)
    return json.dumps(db_path)


@router.get("/result/{dispatch_id}")
def get_result(dispatch_id, wait: Optional[bool], status_only: Optional[bool]):
    # args = request.args
    # wait = args.get("wait", default=False, type=lambda v: v.lower() == "true")
    # status_only = args.get("status_only", default=False, type=lambda v: v.lower() == "true")
    while True:
        with Session(DispatchDB()._get_data_store().engine) as session:
            lattice_record = (
                session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
            )
        try:
            if not lattice_record:
                return (
                    JSONResponse(
                        {"message": f"The requested dispatch ID {dispatch_id} was not found."}
                    ),
                    404,
                )
            elif not wait or lattice_record.status in [
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
                        pickle.dumps(result_from(lattice_record)), "base64"
                    ).decode()
                return output

        except (FileNotFoundError, EOFError):
            if wait:
                continue
            response = JSONResponse(
                (
                    {
                        "message": "Result not ready to read yet. Please wait for a couple of seconds."
                    }
                ),
                503,
            )
            response.retry_after = 2
            return response
