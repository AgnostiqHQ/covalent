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

""" Serialization/Deserialization methods for Assets """

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any

import cloudpickle

from .._shared_files.schemas.asset import AssetSchema
from .._workflow.transportable_object import TransportableObject

__all__ = [
    "AssetType",
    "save_asset",
    "load_asset",
]


CHECKSUM_ALGORITHM = "sha"


class AssetType(Enum):
    """
    Enum for the type of Asset data

    """

    OBJECT = 0  # Fallback to cloudpickling
    TRANSPORTABLE = 1  # Custom TO serialization
    JSONABLE = 2
    TEXT = 3  # Mainly for stdout, stderr, docstrings, etc.
    BYTES = 4  # Just bytes, used for qelectron DB, and other binary data


def serialize_asset(data: Any, data_type: AssetType) -> bytes:
    """
    Serialize the asset data

    Args:
        data: Data to serialize
        data_type: Type of the Asset data to serialize

    Returns:
        Serialized data as bytes

    """

    if data_type == AssetType.OBJECT:
        return cloudpickle.dumps(data)
    elif data_type == AssetType.TRANSPORTABLE:
        return data.serialize()
    elif data_type == AssetType.JSONABLE:
        return json.dumps(data).encode("utf-8")
    elif data_type == AssetType.TEXT:
        return data.encode("utf-8")
    elif data_type == AssetType.BYTES:
        return data
    else:
        raise TypeError(f"Unsupported data type {type(data)}")


def deserialize_asset(data: bytes, data_type: AssetType) -> Any:
    """
    Deserialize the asset data

    Args:
        data: Data to deserialize
        data_type: Type of the Asset data to deserialize

    Returns:
        Deserialized data

    """

    if data_type == AssetType.OBJECT:
        return cloudpickle.loads(data)
    elif data_type == AssetType.TRANSPORTABLE:
        return TransportableObject.deserialize(data)
    elif data_type == AssetType.JSONABLE:
        return json.loads(data.decode("utf-8"))
    elif data_type == AssetType.TEXT:
        return data.decode("utf-8")
    elif data_type == AssetType.BYTES:
        return data
    else:
        raise TypeError("Unsupported data type")


def _sha1_asset(data: bytes) -> str:
    """
    Compute the sha1 checksum of the asset data

    Args:
        data: Data to compute checksum for

    Returns:
        sha1 checksum of the data

    """

    return hashlib.sha1(data).hexdigest()


def save_asset(data: Any, data_type: AssetType, storage_path: str, filename: str) -> AssetSchema:
    """
    Save the asset data to the storage path

    Args:
        data: Data to save
        data_type: Type of the Asset data to save
        storage_path: Path to save the data to
        filename: Name of the file to save the data to

    Returns:
        AssetSchema object containing metadata about the saved data

    """

    scheme = "file"

    serialized = serialize_asset(data, data_type)
    digest = _sha1_asset(serialized)
    path = Path(storage_path) / filename
    path = path.resolve()
    with open(path, "wb") as f:
        f.write(serialized)
    uri = f"{scheme}://{path}"
    return AssetSchema(digest_alg=CHECKSUM_ALGORITHM, digest=digest, size=len(serialized), uri=uri)


def load_asset(asset_meta: AssetSchema, data_type: AssetType) -> Any:
    """
    Load the asset data from the storage path

    Args:
        asset_meta: Metadata about the asset to load
        data_type: Type of the Asset data to load

    Returns:
        Asset data

    """

    scheme_prefix = "file://"
    uri = asset_meta.uri

    if not uri:
        return None

    path = uri[len(scheme_prefix) :] if uri.startswith(scheme_prefix) else uri

    with open(path, "rb") as f:
        data = f.read()
    return deserialize_asset(data, data_type)
