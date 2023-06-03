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
from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

import covalent_dispatcher.entry_point as dispatcher
from covalent._results_manager.result import Result
from covalent._shared_files import logger
from covalent._shared_files.schemas.result import ResultSchema

from .._dal.export import export_result_manifest, export_serialized_result
from .._db.datastore import workflow_db
from .._db.models import Lattice
from .models import ExportResponseSchema

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

_background_tasks = set()


@router.post("/dispatchv2/submit")
async def submitv0(request: Request) -> UUID:
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


@router.post("/dispatchv2/register")
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


@router.post("/dispatchv2/register/{dispatch_id}")
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


@router.post("/dispatchv2/resubmit")
async def resubmit(request: Request) -> str:
    """Endpoint to redispatch a workflow."""
    try:
        data = await request.json()
        dispatch_id = data["dispatch_id"]
        json_lattice = data["json_lattice"]
        electron_updates = data["electron_updates"]
        reuse_previous_results = data["reuse_previous_results"]
        return await dispatcher.make_redispatch(
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


@router.put("/dispatchv2/start/{dispatch_id}")
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


@router.get("/resultv2/{dispatch_id}")
async def get_result_v2(
    dispatch_id: str, wait: Optional[bool] = False, status_only: Optional[bool] = False
):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _get_result_v2_sync,
        dispatch_id,
        wait,
        status_only,
    )


def _get_result_v2_sync(
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
                output["result_export"] = export_serialized_result(dispatch_id)

            return output

        response = JSONResponse(
            status_code=503,
            content={
                "message": "Result not ready to read yet. Please wait for a couple of seconds."
            },
            headers={"Retry-After": "2"},
        )
        return response


@router.get("/export/{dispatch_id}")
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
