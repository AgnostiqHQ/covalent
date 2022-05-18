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
from typing import Any, List

import boto3
from app.core.config import settings
from app.schemas.common import HTTPExceptionSchema
from app.schemas.fs import DeleteResponse, UploadResponse
from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from minio import Minio

from ....core.localstoragebackend import LocalStorageBackend
from ....core.miniostoragebackend import MinioStorageBackend
from ....core.s3storagebackend import S3StorageBackend

router = APIRouter()

MINIO_USE_TLS = settings.MINIO_DISABLE_TLS.lower() not in ("true", "1")

minio_client = None
# TODO: support additional minio config options
if settings.FS_STORAGE_BACKEND == "minio":
    minio_client = Minio(
        endpoint=settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=MINIO_USE_TLS,
    )
    backend = MinioStorageBackend(minio_client, settings.FS_STORAGE_BUCKET)
elif settings.FS_STORAGE_BACKEND == "s3":
    # Reads AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION from environment vars
    backend = S3StorageBackend(settings.FS_STORAGE_BUCKET)
else:
    backend = LocalStorageBackend(Path(settings.FS_LOCAL_STORAGE_ROOT), settings.FS_STORAGE_BUCKET)


@router.post("/upload", status_code=200, response_model=UploadResponse)
def upload_file(*, file: UploadFile, overwrite: bool = False) -> Any:
    """
    Upload a file
    """

    file.file.seek(0, 2)
    length = file.file.tell()
    file.file.seek(0)

    path, filename = backend.put(
        file.file, backend.bucket_name, file.filename, length, overwrite=overwrite
    )

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
    stream = backend.get(backend.bucket_name, file_location)
    if not stream:
        raise HTTPException(status_code=404, detail="File not found")

    return StreamingResponse(
        stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{file_location}"'},
    )


@router.delete("/delete", status_code=200, response_model=DeleteResponse)
def delete_file(*, obj_names: List[str] = Query([])) -> DeleteResponse:
    deleted, failed = backend.delete(backend.bucket_name, obj_names)
    return {
        "deleted": deleted,
        "failed": failed,
    }
