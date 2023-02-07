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
import shutil
from typing import Optional

from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from covalent._results_manager.result import Result
from covalent._shared_files import logger

from .._dal.export import export_serialized_result, get_dispatch_asset_uri, get_node_asset_uri
from .._db.datastore import workflow_db
from .._db.models import Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()


@router.get("/resultv2/{dispatch_id}")
def get_result_v2(
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


@router.get("/resultv2/{dispatch_id}/assets/node/{node_id}/{key}")
async def get_node_asset_exp(
    dispatch_id: str,
    node_id: int,
    key: str,
):
    app_log.debug(f"Requested asset {key} for node {dispatch_id}:{node_id}")

    with workflow_db.session() as session:
        lattice_record = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
        status = lattice_record.status if lattice_record else None
        if not lattice_record:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

    try:
        path = get_node_asset_uri(dispatch_id, node_id, key)
    except:
        return JSONResponse(
            status_code=404,
            content={"message": f"Error retrieving asset {key}."},
        )
    return FileResponse(path)


@router.get("/resultv2/{dispatch_id}/assets/dispatch/{key}")
async def get_dispatch_asset_exp(
    dispatch_id: str,
    key: str,
):
    app_log.debug(f"Requested asset {key} for dispatch {dispatch_id}")

    with workflow_db.session() as session:
        lattice_record = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
        status = lattice_record.status if lattice_record else None
        if not lattice_record:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

    try:
        path = get_dispatch_asset_uri(dispatch_id, key)
        app_log.debug(f"Dispatch result uri: {path}")
    except:
        return JSONResponse(
            status_code=404,
            content={"message": f"Error retrieving asset {key}."},
        )
    return FileResponse(path)


# Demo only!!!
@router.post("/resultv2/{dispatch_id}/assets/node/{node_id}/{key}")
async def upload_node_asset_exp(dispatch_id: str, node_id: int, key: str, asset_file: UploadFile):
    app_log.debug(f"Requested asset {key} for node {dispatch_id}:{node_id}")

    with workflow_db.session() as session:
        lattice_record = session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
        status = lattice_record.status if lattice_record else None
        if not lattice_record:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

    try:
        path = get_node_asset_uri(dispatch_id, node_id, key)
    except:
        return JSONResponse(
            status_code=404,
            content={"message": f"Error retrieving metadata for asset {key}."},
        )

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _copy_file_obj, asset_file.file, path)

    return f"Uploaded file to {path}"


def _copy_file_obj(src_fileobj, dest_path):
    with open(dest_path, "wb") as dest_fileobj:
        shutil.copyfileobj(src_fileobj, dest_fileobj)
