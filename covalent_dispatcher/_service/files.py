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
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from covalent._shared_files import logger
from covalent._shared_files.config import get_config

router = APIRouter()

app_log = logger.app_log
BASE_PATH = get_config("dispatcher.results_dir")


def _generate_file_slice(file_path: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
    """Generator of a byte slice from a file.

    Args:
        path: An absolute path to the file
        start_byte: The beginning of the byte range
        end_byte: The end of the byte range, or -1 to select [start_byte:]
        chunk_size: The size of each chunk

    Returns:
        Yields chunks of size <= chunk_size
    """
    byte_pos = start_byte
    with open(file_path, "rb") as f:
        f.seek(start_byte)
        if end_byte < 0:
            for chunk in f:
                yield chunk
        else:
            while byte_pos + chunk_size < end_byte:
                byte_pos += chunk_size
                yield f.read(chunk_size)
            yield f.read(end_byte - byte_pos)


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
def download_file(object_key: str):
    # TODO: reject relative path components

    start_byte = 0
    end_byte = -1

    path = os.path.join(BASE_PATH, object_key)
    generator = _generate_file_slice(path, start_byte, end_byte)

    return StreamingResponse(generator)


@router.put("/files/{object_key:path}")
async def upload_file(req: Request, object_key: str):
    # TODO: reject relative path components

    path = os.path.join(BASE_PATH, object_key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    await _transfer_data(req, path)
