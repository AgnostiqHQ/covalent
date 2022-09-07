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
from typing import Optional
from uuid import UUID

import cloudpickle as pickle
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import covalent_dispatcher as dispatcher
from covalent._data_store.datastore import workflow_db
from covalent._data_store.models import Lattice
from covalent._results_manager.result import Result
from covalent._results_manager.results_manager import result_from
from covalent._shared_files import logger

from .._db.dispatchdb import DispatchDB

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()


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
    data = await request.json()
    data = json.dumps(data).encode("utf-8")

    dispatch_id = await dispatcher.run_dispatcher(data)
    return dispatch_id


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
    data = await request.body()
    dispatch_id = data.decode("utf-8")

    dispatcher.cancel_running_dispatch(dispatch_id)
    return f"Dispatch {dispatch_id} cancelled."


@router.get("/db-path")
def db_path() -> str:
    db_path = DispatchDB()._dbpath
    return json.dumps(db_path)


@router.get("/result/{dispatch_id}")
def get_result(
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
                    pickle.dumps(result_from(lattice_record)), "base64"
                ).decode()
            return output

        response = JSONResponse(
            status_code=503,
            content={
                "message": "Result not ready to read yet. Please wait for a couple of seconds."
            },
            headers={"Retry-After": "2"},
        )
        return response
