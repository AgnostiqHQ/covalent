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
import io
import json
import os
import random
import sqlite3
import string
import time
from os import path
from tempfile import TemporaryFile
from typing import Any, BinaryIO, List, Optional, Tuple, Union

import cloudpickle as pickle
import requests
from aiohttp import ClientSession
from app.core.api import DataService
from app.core.config import settings
from app.core.db import Database
from app.core.get_svc_uri import DataURI
from app.schemas.common import HTTPExceptionSchema
from app.schemas.workflow import (
    DeleteResultResponse,
    InsertResultResponse,
    Node,
    Result,
    ResultFormats,
    UpdateResultResponse,
)
from fastapi import APIRouter, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.responses import FileResponse, StreamingResponse

from covalent._shared_files.utils import encode_result

router = APIRouter()

data_svc = DataService()
db = Database()


# @router.middleware("http")
# TODO: figure out why the middleware doesn't work
# async def log_requests(request: Request, call_next):
#    idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
#    logger.info(f"rid={idem} start request path={request.url.path}")
#    start_time = time.time()
#
#    response = await call_next(request)
#
#    process_time = (time.time() - start_time) * 1000
#    formatted_process_time = "{0:.2f}".format(process_time)
#    logger.info(
#        f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
#    )
#
#    return response


async def _get_result_file(dispatch_id: str) -> bytes:
    filename = _get_result_from_db(dispatch_id, "filename")
    path = _get_result_from_db(dispatch_id, "path")
    if not dispatch_id or not filename or not path:
        raise HTTPException(status_code=404, detail="Result was not found")
    file = await data_svc.download(filename)
    return file


async def _upload_file(result_pkl_file: BinaryIO):
    results_object = {}
    dispatch_id = ""
    length = result_pkl_file.seek(0, 2)
    result_pkl_file.seek(0)
    try:
        results_object = pickle.load(result_pkl_file)
        dispatch_id = results_object.dispatch_id
        assert length > 0
    except:
        raise HTTPException(status_code=422, detail="Error in upload body.")
    result_pkl_file.seek(0)
    response = await data_svc.upload(result_pkl_file)
    filename = response.get("filename")
    path = response.get("path")
    error_detail = "Error in response from data service. " + str(response)
    if filename and path:
        if _add_record_to_db(dispatch_id, filename, path):
            return {"dispatch_id": dispatch_id}
        else:
            error_detail = "Error adding record to database."
    raise HTTPException(status_code=500, detail="Error adding record to database.")


async def _concurrent_download_and_serialize(semaphore, file_name, session):
    async with semaphore:
        # logger.debug(f"Downloading & serializing: {file_name}...")
        async with session.get(
            DataURI().get_route("/fs/download"), params={"file_location": file_name}
        ) as resp:
            result_binary = await resp.read()
            result = pickle.loads(result_binary)
            result_json = json.loads(encode_result(result))
            return result_json


def _get_results_from_db() -> List[Tuple[str, str]]:
    con = sqlite3.connect(settings.RESULTS_DB)
    cur = con.cursor()
    cur.execute("SELECT dispatch_id, filename FROM results")
    rows = cur.fetchall()
    return rows


def _get_result_from_db(dispatch_id: str, field: str) -> Optional[str]:
    sql = f"SELECT {field} FROM results WHERE dispatch_id=?"
    value = db.value(sql, key=dispatch_id)
    if value:
        (value,) = value
    return value


def _add_record_to_db(dispatch_id: str, filename: str, path: str) -> None:
    sql = ""
    if _get_result_from_db(dispatch_id, "filename"):
        sql = (
            "UPDATE results "
            f"SET filename = '{filename}', path = '{path}' "
            f"WHERE dispatch_id = '{dispatch_id}' "
            # f"ORDER BY dispatch_id "
            # "LIMIT 1"
        )
    else:
        sql = f"INSERT INTO results VALUES('{dispatch_id}','{filename}','{path}')"
    insert = db.value(sql)
    if insert:
        (insert,) = insert
    return insert


@router.get(
    "/results",
    status_code=200,
    responses={
        200: {
            "model": List[Result],
            "description": "Return JSON serialized result objects from the database",
        },
    },
)
async def get_results(format: ResultFormats = ResultFormats.JSON) -> Any:
    """
    Return JSON serialized result objects from the database
    """
    results = _get_results_from_db()
    tasks = []
    # Set 10 concurrent requests at a time
    semaphore = asyncio.Semaphore(10)
    async with ClientSession() as session:
        # Send requests in parallel to Data Service for download
        for result in results:
            dispatch_id, file_name = result
            task = asyncio.create_task(
                _concurrent_download_and_serialize(semaphore, file_name, session)
            )
            tasks.append(task)
        # Wait until parallel tasks return and gather results
        responses = await asyncio.gather(*tasks, return_exceptions=False)
        return responses


@router.get(
    "/results/{dispatch_id}",
    status_code=200,
    response_class=FileResponse,
    responses={
        404: {"model": HTTPExceptionSchema, "description": "Result was not found"},
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Return binary content of file.",
        },
    },
)
async def get_result(*, dispatch_id: str, format: ResultFormats = ResultFormats.BINARY) -> Any:
    """
    Get a result object as pickle file
    """
    result_binary: bytes = await _get_result_file(dispatch_id)
    if format == ResultFormats.JSON:
        result = pickle.loads(result_binary)
        result_json_stringified = encode_result(result)
        return Response(content=result_json_stringified, media_type="application/json")
    else:
        return StreamingResponse(io.BytesIO(result_binary), media_type="application/octet-stream")


@router.post("/results", status_code=200, response_model=InsertResultResponse)
async def insert_result(
    *,
    result_pkl_file: UploadFile,
) -> Any:
    """
    Submit pickled result file
    """

    response = await _upload_file(result_pkl_file.file)
    return response


@router.put(
    "/results/{dispatch_id}",
    status_code=200,
    responses={
        404: {"model": HTTPExceptionSchema, "description": "Result was not found"},
        200: {
            "model": UpdateResultResponse,
            "description": "Return message indicating success of updating task",
        },
    },
)
async def update_result(*, dispatch_id: str, task: bytes = File(...)) -> Any:
    """
    Update a result object's task
    """
    result = await _get_result_file(dispatch_id)
    results_object = pickle.loads(result)
    task = pickle.loads(task)
    results_object._update_node(**task)

    pickled_result = io.BytesIO(pickle.dumps(results_object))
    uploaded = await _upload_file(pickled_result)

    if uploaded:
        return {"response": "Task updated successfully"}


@router.delete("/results", status_code=200, response_model=DeleteResultResponse)
def delete_result(*, dispatch_ids: List[str] = Query([])) -> DeleteResultResponse:
    # Retrieve file paths from db
    filenames = []

    # TODO: add batch method to request set of results
    for dispatch_id in dispatch_ids:
        filenames += [_get_result_from_db(dispatch_id, "filename")]

    # Request deletion from the data service
    r = requests.delete(DataURI().get_route("/fs/delete"), params={"obj_names": filenames})

    deleted_results = r.json()["deleted"]

    deleted_ids = []
    failed_ids = []
    sql = "DELETE FROM results WHERE dispatch_id = ?"
    # TODO: perform this in a single SQL command
    for idx, dispatch_id in enumerate(dispatch_ids):
        if filenames[idx] in deleted_results:
            deleted_ids.append(dispatch_id)
            db.value(sql, dispatch_id)
        else:
            failed_ids.append(dispatch_id)

    return {
        "deleted": deleted_ids,
        "failed": failed_ids,
    }
