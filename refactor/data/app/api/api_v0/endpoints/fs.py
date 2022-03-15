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


from pathlib import Path
from typing import Any

from app.schemas.common import HTTPExceptionSchema
from app.schemas.fs import UploadResponse
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio

from ....core.localstoragebackend import LocalStorageBackend
from ....core.miniostoragebackend import MinioStorageBackend

router = APIRouter()

# Initialize backend from config
backend = LocalStorageBackend(Path("data"))
# minio_client = Minio(
#     "localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
# )
# backend = MinioStorageBackend(minio_client)


@router.post("/upload", status_code=200, response_model=UploadResponse)
def upload_file(*, file: UploadFile) -> Any:
    """
    Upload a file
    """

    file.file.seek(0, 2)
    length = file.file.tell()
    file.file.seek(0)

    path, filename = backend.put(file.file, backend.bucket_name, file.filename, length)
    print("DEBUG: ", path, filename)

    return {
        "filename": filename,
        "path": path,
    }


@router.get(
    "/download",
    status_code=200,
    response_class=StreamingResponse,
    responses={
        404: {"model": HTTPExceptionSchema, "description": "File was not found"},
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Return binary content of file.",
        },
    },
)
def download_file(*, file_location: str) -> Any:
    """
    Download a file
    """
    g = backend.get(backend.bucket_name, file_location)
    if not g:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(g, media_type="application/octet-stream")
