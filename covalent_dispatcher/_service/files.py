# Copyright 2024 Agnostiq Inc.
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

"""Embedded file server API"""

import os

import aiofiles
import aiofiles.os
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse

from covalent._shared_files import logger
from covalent._shared_files.config import get_config

router = APIRouter()

app_log = logger.app_log
BASE_PATH = get_config("dispatcher.results_dir")


async def _transfer_data(req: Request, dest_path: str):

    # Stream data to a temporary file, then replace the destination
    # file atomically
    tmp_path = f"{dest_path}.tmp"
    app_log.debug(f"Streaming file upload to {tmp_path}")

    async with aiofiles.open(tmp_path, "wb") as f:
        async for chunk in req.stream():
            await f.write(chunk)

    await aiofiles.os.replace(tmp_path, dest_path)


@router.get("/files/{object_key:path}")
async def download_file(object_key: str):
    # TODO: reject relative path components

    path = os.path.join(BASE_PATH, object_key)
    return FileResponse(path)


@router.put("/files/{object_key:path}")
async def upload_file(req: Request, object_key: str):
    # TODO: reject relative path components

    path = os.path.join(BASE_PATH, object_key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    await _transfer_data(req, path)
