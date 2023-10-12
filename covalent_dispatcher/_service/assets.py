# Copyright 2021 Agnostiq Inc.
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

"""Endpoints for uploading and downloading workflow assets"""

import asyncio
import mmap
import os
from functools import lru_cache
from typing import Tuple, Union

import aiofiles
import aiofiles.os
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from furl import furl

from covalent._serialize.electron import ASSET_TYPES as ELECTRON_ASSET_TYPES
from covalent._serialize.lattice import ASSET_TYPES as LATTICE_ASSET_TYPES
from covalent._serialize.result import ASSET_TYPES as RESULT_ASSET_TYPES
from covalent._serialize.result import AssetType
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._workflow.transportable_object import TOArchiveUtils

from .._dal.result import get_result_object
from .._db.datastore import workflow_db
from .models import (
    AssetRepresentation,
    DispatchAssetKey,
    ElectronAssetKey,
    LatticeAssetKey,
    range_pattern,
    range_regex,
)

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router: APIRouter = APIRouter()

_background_tasks = set()

LRU_CACHE_SIZE = get_config("dispatcher.asset_cache_size")


@router.get("/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
def get_node_asset(
    dispatch_id: str,
    node_id: int,
    key: ElectronAssetKey,
    representation: Union[AssetRepresentation, None] = None,
    Range: Union[str, None] = Header(default=None, regex=range_regex),
):
    """Returns an asset for an electron.

    Args:
        dispatch_id: The dispatch's unique id.
        node_id: The id of the electron.
        key: The name of the asset
        representation: (optional) the representation ("string" or "pickle") of a `TransportableObject`
        range: (optional) range request header

    If `representation` is specified, it will override the range request.
    """
    start_byte = 0
    end_byte = -1

    try:
        if Range:
            start_byte, end_byte = _extract_byte_range(Range)

        if end_byte >= 0 and end_byte < start_byte:
            raise HTTPException(
                status_code=400,
                detail="Invalid byte range",
            )
        app_log.debug(
            f"Requested asset {key.value} ([{start_byte}:{end_byte}]) for node {dispatch_id}:{node_id}"
        )

        result_object = get_cached_result_object(dispatch_id)

        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")

        node = result_object.lattice.transport_graph.get_node(node_id)
        with workflow_db.session() as session:
            asset = node.get_asset(key=key.value, session=session)

        # Explicit representation overrides the byte range
        if representation is None or ELECTRON_ASSET_TYPES[key.value] != AssetType.TRANSPORTABLE:
            start_byte = start_byte
            end_byte = end_byte
        elif representation == AssetRepresentation.string:
            start_byte, end_byte = _get_tobj_string_offsets(asset.internal_uri)
        else:
            start_byte, end_byte = _get_tobj_pickle_offsets(asset.internal_uri)

        app_log.debug(f"Serving byte range {start_byte}:{end_byte} of {asset.internal_uri}")
        generator = _generate_file_slice(asset.internal_uri, start_byte, end_byte)
        return StreamingResponse(generator)

    except Exception as e:
        app_log.debug(e)
        raise


@router.get("/dispatches/{dispatch_id}/assets/{key}")
def get_dispatch_asset(
    dispatch_id: str,
    key: DispatchAssetKey,
    representation: Union[AssetRepresentation, None] = None,
    Range: Union[str, None] = Header(default=None, regex=range_regex),
):
    """Returns a dynamic asset for a workflow

    Args:
        dispatch_id: The dispatch's unique id.
        key: The name of the asset
        representation: (optional) the representation ("string" or "pickle") of a `TransportableObject`
        range: (optional) range request header

    If `representation` is specified, it will override the range request.
    """
    start_byte = 0
    end_byte = -1

    try:
        if Range:
            start_byte, end_byte = _extract_byte_range(Range)

        if end_byte >= 0 and end_byte < start_byte:
            raise HTTPException(
                status_code=400,
                detail="Invalid byte range",
            )
        app_log.debug(
            f"Requested asset {key.value} ([{start_byte}:{end_byte}]) for dispatch {dispatch_id}"
        )

        result_object = get_cached_result_object(dispatch_id)

        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
        with workflow_db.session() as session:
            asset = result_object.get_asset(key=key.value, session=session)

        # Explicit representation overrides the byte range
        if representation is None or RESULT_ASSET_TYPES[key.value] != AssetType.TRANSPORTABLE:
            start_byte = start_byte
            end_byte = end_byte
        elif representation == AssetRepresentation.string:
            start_byte, end_byte = _get_tobj_string_offsets(asset.internal_uri)
        else:
            start_byte, end_byte = _get_tobj_pickle_offsets(asset.internal_uri)

        app_log.debug(f"Serving byte range {start_byte}:{end_byte} of {asset.internal_uri}")
        generator = _generate_file_slice(asset.internal_uri, start_byte, end_byte)
        return StreamingResponse(generator)
    except Exception as e:
        app_log.debug(e)
        raise


@router.get("/dispatches/{dispatch_id}/lattice/assets/{key}")
def get_lattice_asset(
    dispatch_id: str,
    key: LatticeAssetKey,
    representation: Union[AssetRepresentation, None] = None,
    Range: Union[str, None] = Header(default=None, regex=range_regex),
):
    """Returns a static asset for a workflow

    Args:
        dispatch_id: The dispatch's unique id.
        key: The name of the asset
        representation: (optional) the representation ("string" or "pickle") of a `TransportableObject`
        range: (optional) range request header

    If `representation` is specified, it will override the range request.
    """
    start_byte = 0
    end_byte = -1

    try:
        if Range:
            start_byte, end_byte = _extract_byte_range(Range)

        if end_byte >= 0 and end_byte < start_byte:
            raise HTTPException(
                status_code=400,
                detail="Invalid byte range",
            )
        app_log.debug(
            f"Requested lattice asset {key.value} ([{start_byte}:{end_byte}])for dispatch {dispatch_id}"
        )

        result_object = get_cached_result_object(dispatch_id)
        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")

        with workflow_db.session() as session:
            asset = result_object.lattice.get_asset(key=key.value, session=session)

        # Explicit representation overrides the byte range
        if representation is None or LATTICE_ASSET_TYPES[key.value] != AssetType.TRANSPORTABLE:
            start_byte = start_byte
            end_byte = end_byte
        elif representation == AssetRepresentation.string:
            start_byte, end_byte = _get_tobj_string_offsets(asset.internal_uri)
        else:
            start_byte, end_byte = _get_tobj_pickle_offsets(asset.internal_uri)

        app_log.debug(f"Serving byte range {start_byte}:{end_byte} of {asset.internal_uri}")
        generator = _generate_file_slice(asset.internal_uri, start_byte, end_byte)
        return StreamingResponse(generator)

    except Exception as e:
        app_log.debug(e)
        raise e


@router.put("/dispatches/{dispatch_id}/electrons/{node_id}/assets/{key}")
async def upload_node_asset(
    req: Request,
    dispatch_id: str,
    node_id: int,
    key: ElectronAssetKey,
    content_length: int = Header(default=0),
    digest_alg: Union[str, None] = Header(default=None),
    digest: Union[str, None] = Header(default=None),
):
    """Upload an electron asset.

    Args:
        dispatch_id: The dispatch's unique id.
        node_id: The electron id.
        key: The name of the asset
        asset_file: (body) The file to be uploaded
        content_length: (header)
        digest: (header)
    """
    app_log.debug(f"Requested asset {key} for node {dispatch_id}:{node_id}")

    try:
        metadata = {"size": content_length, "digest_alg": digest_alg, "digest": digest}
        internal_uri = await _run_in_executor(
            _update_node_asset_metadata,
            dispatch_id,
            node_id,
            key,
            metadata,
        )
        # Stream the request body to object store
        await _transfer_data(req, internal_uri)

        return f"Uploaded file to {internal_uri}"
    except Exception as e:
        app_log.debug(e)
        raise


@router.put("/dispatches/{dispatch_id}/assets/{key}")
async def upload_dispatch_asset(
    req: Request,
    dispatch_id: str,
    key: DispatchAssetKey,
    content_length: int = Header(default=0),
    digest_alg: Union[str, None] = Header(default=None),
    digest: Union[str, None] = Header(default=None),
):
    """Upload a dispatch asset.

    Args:
        dispatch_id: The dispatch's unique id.
        key: The name of the asset
        asset_file: (body) The file to be uploaded
        content_length: (header)
        digest: (header)
    """
    try:
        metadata = {"size": content_length, "digest_alg": digest_alg, "digest": digest}
        internal_uri = await _run_in_executor(
            _update_dispatch_asset_metadata,
            dispatch_id,
            key,
            metadata,
        )
        # Stream the request body to object store
        await _transfer_data(req, internal_uri)
        return f"Uploaded file to {internal_uri}"
    except Exception as e:
        app_log.debug(e)
        raise


@router.put("/dispatches/{dispatch_id}/lattice/assets/{key}")
async def upload_lattice_asset(
    req: Request,
    dispatch_id: str,
    key: LatticeAssetKey,
    content_length: int = Header(default=0),
    digest_alg: Union[str, None] = Header(default=None),
    digest: Union[str, None] = Header(default=None),
):
    """Upload a lattice asset.

    Args:
        dispatch_id: The dispatch's unique id.
        key: The name of the asset
        asset_file: (body) The file to be uploaded
        content_length: (header)
        digest: (header)
    """
    try:
        metadata = {"size": content_length, "digest_alg": digest_alg, "digest": digest}
        internal_uri = await _run_in_executor(
            _update_lattice_asset_metadata,
            dispatch_id,
            key,
            metadata,
        )
        # Stream the request body to object store
        await _transfer_data(req, internal_uri)
        return f"Uploaded file to {internal_uri}"
    except Exception as e:
        app_log.debug(e)
        raise


def _generate_file_slice(file_url: str, start_byte: int, end_byte: int, chunk_size: int = 65536):
    """Generator of a byte slice from a file.

    Args:
        file_url: A file:/// type URL pointing to the file
        start_byte: The beginning of the byte range
        end_byte: The end of the byte range, or -1 to select [start_byte:]
        chunk_size: The size of each chunk

    Returns:
        Yields chunks of size <= chunk_size
    """
    byte_pos = start_byte
    file_path = str(furl(file_url).path)
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


def _extract_byte_range(byte_range_header: str) -> Tuple[int, int]:
    """Extract the byte range from a range request header."""
    start_byte = 0
    end_byte = -1
    match = range_pattern.match(byte_range_header)
    start = match.group(1)
    end = match.group(2)
    start_byte = int(start)
    if end:
        end_byte = int(end)

    return start_byte, end_byte


# Helpers for TransportableObject


def _get_tobj_string_offsets(file_url: str) -> Tuple[int, int]:
    """Get the byte range for the str rep of a stored TObj.

    For a first implementation we just query the filesystem directly.

    Args:
        file_url: A file:/// URL pointing to the TransportableObject

    Returns:
        (start_byte, end_byte)
    """

    file_path = str(furl(file_url).path)
    filelen = os.path.getsize(file_path)
    with open(file_path, "rb+") as f:
        with mmap.mmap(f.fileno(), filelen) as mm:
            # TOArchiveUtils operates on byte arrays
            return TOArchiveUtils.string_byte_range(mm)


def _get_tobj_pickle_offsets(file_url: str) -> Tuple[int, int]:
    """Get the byte range for the picklebytes of a stored TObj.

    For a first implementation we just query the filesystem directly.

    Args:
        file_url: A file:/// URL pointing to the TransportableObject

    Returns:
        (start_byte, -1)
    """

    file_path = str(furl(file_url).path)
    filelen = os.path.getsize(file_path)
    with open(file_path, "rb+") as f:
        with mmap.mmap(f.fileno(), filelen) as mm:
            # TOArchiveUtils operates on byte arrays
            return TOArchiveUtils.data_byte_range(mm)


# This must only be used for static data as we don't have yet any
# intelligent invalidation logic.
@lru_cache(maxsize=LRU_CACHE_SIZE)
def get_cached_result_object(dispatch_id: str):
    try:
        with workflow_db.session() as session:
            srv_res = get_result_object(dispatch_id, bare=False, session=session)
            app_log.debug(f"Caching result {dispatch_id}")

            # Prepopulate asset maps to avoid DB lookups

            srv_res.populate_asset_map(session)
            srv_res.lattice.populate_asset_map(session)

            tg = srv_res.lattice.transport_graph
            g = tg.get_internal_graph_copy()
            for node_id in g.nodes():
                node = tg.get_node(node_id, session)
                node.populate_asset_map(session)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"The requested dispatch ID {dispatch_id} was not found.",
        )

    return srv_res


def _filter_null_metadata(metadata):
    # Filter out null updates
    return {k: v for k, v in metadata.items() if v is not None}


def _update_node_asset_metadata(dispatch_id, node_id, key, metadata) -> str:
    result_object = get_cached_result_object(dispatch_id)

    app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
    node = result_object.lattice.transport_graph.get_node(node_id)
    with workflow_db.session() as session:
        asset = node.get_asset(key=key.value, session=session)
        app_log.debug(f"Asset uri {asset.internal_uri}")

        # Update asset metadata
        update = _filter_null_metadata(metadata)
        node.update_assets(updates={key: update}, session=session)
        app_log.debug(f"Updated node asset {dispatch_id}:{node_id}:{key}")

        return asset.internal_uri


def _update_lattice_asset_metadata(dispatch_id, key, metadata) -> str:
    result_object = get_cached_result_object(dispatch_id)

    app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
    with workflow_db.session() as session:
        asset = result_object.lattice.get_asset(key=key.value, session=session)

        # Update asset metadata
        update = _filter_null_metadata(metadata)
        result_object.lattice.update_assets(updates={key: update}, session=session)
        app_log.debug(f"Updated size for lattice asset {dispatch_id}:{key}")

        return asset.internal_uri


def _update_dispatch_asset_metadata(dispatch_id, key, metadata) -> str:
    result_object = get_cached_result_object(dispatch_id)

    app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
    with workflow_db.session() as session:
        asset = result_object.get_asset(key=key.value, session=session)

        # Update asset metadata
        update = _filter_null_metadata(metadata)
        result_object.update_assets(updates={key: update}, session=session)
        app_log.debug(f"Updated size for dispatch asset {dispatch_id}:{key}")
        return asset.internal_uri


async def _transfer_data(req: Request, destination_url: str):
    dest_url = furl(destination_url)
    dest_path = str(dest_url.path)

    # Stream data to a temporary file, then replace the destination
    # file atomically
    tmp_path = f"{dest_path}.tmp"

    async with aiofiles.open(tmp_path, "wb") as f:
        async for chunk in req.stream():
            await f.write(chunk)

    await aiofiles.os.replace(tmp_path, dest_path)


def _run_in_executor(function, *args) -> asyncio.Future:
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, function, *args)
