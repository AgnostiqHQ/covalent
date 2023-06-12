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

"""Endpoints for uploading and downloading workflow assets"""

import mmap
import os
import shutil
from functools import lru_cache
from typing import BinaryIO, Tuple, Union

from fastapi import APIRouter, Header, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
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
    digest_pattern,
    digest_regex,
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


@router.get("/assets/{dispatch_id}/node/{node_id}/{key}")
def get_node_asset(
    dispatch_id: str,
    node_id: int,
    key: ElectronAssetKey,
    representation: Union[AssetRepresentation, None] = None,
    Range: Union[str, None] = Header(default=None, regex=range_regex),
):
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
        if not result_object:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

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


@router.get("/assets/{dispatch_id}/dispatch/{key}")
def get_dispatch_asset(
    dispatch_id: str,
    key: DispatchAssetKey,
    representation: Union[AssetRepresentation, None] = None,
    Range: Union[str, None] = Header(default=None, regex=range_regex),
):
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
        if not result_object:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

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


@router.get("/assets/{dispatch_id}/lattice/{key}")
def get_lattice_asset(
    dispatch_id: str,
    key: LatticeAssetKey,
    representation: Union[AssetRepresentation, None] = None,
    Range: Union[str, None] = Header(default=None, regex=range_regex),
):
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
        if not result_object:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )
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


@router.post("/assets/{dispatch_id}/node/{node_id}/{key}")
def upload_node_asset(
    dispatch_id: str,
    node_id: int,
    key: ElectronAssetKey,
    asset_file: UploadFile,
    content_length: int = Header(),
    digest: Union[str, None] = Header(default=None, regex=digest_regex),
):
    app_log.debug(f"Requested asset {key} for node {dispatch_id}:{node_id}")

    try:
        result_object = get_cached_result_object(dispatch_id)
        if not result_object:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
        node = result_object.lattice.transport_graph.get_node(node_id)
        with workflow_db.session() as session:
            asset = node.get_asset(key=key.value, session=session)
            app_log.debug(f"Asset uri {asset.internal_uri}")

            # Update asset metadata
            update = {"size": content_length}
            if digest:
                alg, checksum = _extract_checksum(digest)
                update["digest_alg"] = alg
                update["digest"] = checksum
            node.update_assets(updates={key: update}, session=session)
            app_log.debug(f"Updated node asset {dispatch_id}:{node_id}:{key}")

        # Copy the tempfile to object store
        _copy_file_obj(asset_file.file, asset.internal_uri)

        return f"Uploaded file to {asset.internal_uri}"
    except Exception as e:
        app_log.debug(e)
        raise


@router.post("/assets/{dispatch_id}/dispatch/{key}")
def upload_dispatch_asset(
    dispatch_id: str,
    key: DispatchAssetKey,
    asset_file: UploadFile,
    content_length: int = Header(),
    digest: Union[str, None] = Header(default=None, regex=digest_regex),
):
    try:
        result_object = get_cached_result_object(dispatch_id)
        if not result_object:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")
        with workflow_db.session() as session:
            asset = result_object.get_asset(key=key.value, session=session)

            # Update asset metadata
            update = {"size": content_length}
            if digest:
                alg, checksum = _extract_checksum(digest)
                update["digest_alg"] = alg
                update["digest"] = checksum
            result_object.update_assets(updates={key: update}, session=session)
            app_log.debug(f"Updated size for dispatch asset {dispatch_id}:{key}")

        # Copy the tempfile to object store
        _copy_file_obj(asset_file.file, asset.internal_uri)

        return f"Uploaded file to {asset.internal_uri}"
    except Exception as e:
        app_log.debug(e)
        raise


@router.post("/assets/{dispatch_id}/lattice/{key}")
def upload_lattice_asset(
    dispatch_id: str,
    key: LatticeAssetKey,
    asset_file: UploadFile,
    content_length: int = Header(),
    digest: Union[str, None] = Header(default=None, regex=digest_regex),
):
    try:
        result_object = get_cached_result_object(dispatch_id)
        if not result_object:
            return JSONResponse(
                status_code=404,
                content={"message": f"The requested dispatch ID {dispatch_id} was not found."},
            )

        app_log.debug(f"LRU cache info: {get_cached_result_object.cache_info()}")

        with workflow_db.session() as session:
            asset = result_object.lattice.get_asset(key=key.value, session=session)

            # Update asset metadata
            update = {"size": content_length}
            if digest:
                alg, checksum = _extract_checksum(digest)
                update["digest_alg"] = alg
                update["digest"] = checksum
            result_object.lattice.update_assets(updates={key: update}, session=session)
            app_log.debug(f"Updated size for lattice asset {dispatch_id}:{key}")

        # Copy the tempfile to object store
        _copy_file_obj(asset_file.file, asset.internal_uri)

        return f"Uploaded file to {asset.internal_uri}"
    except Exception as e:
        app_log.debug(e)
        raise


def _copy_file_obj(src_fileobj: BinaryIO, dest_url: str):
    dest_path = str(furl(dest_url).path)
    with open(dest_path, "wb") as dest_fileobj:
        shutil.copyfileobj(src_fileobj, dest_fileobj)


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


def _extract_checksum(digest_header: str) -> Tuple[str, str]:
    match = digest_pattern.match(digest_header)
    alg = match.group(0)
    checksum = match.group(1)
    return alg, checksum


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
        (start_byte, end_byte)
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
            srv_res = get_result_object(dispatch_id, session=session)
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
        srv_res = None

    return srv_res
