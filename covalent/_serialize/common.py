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


import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any

import cloudpickle

from .._shared_files.schemas.asset import AssetSchema
from .._workflow.transportable_object import TransportableObject

CHECKSUM_ALGORITHM = "sha"


class AssetType(Enum):
    OBJECT = 0
    TRANSPORTABLE = 1
    JSONABLE = 2
    TEXT = 3


def serialize_asset(data: Any, data_type: AssetType) -> bytes:
    if data_type == AssetType.OBJECT:
        return cloudpickle.dumps(data)
    elif data_type == AssetType.TRANSPORTABLE:
        return data.serialize()
    elif data_type == AssetType.JSONABLE:
        return json.dumps(data).encode("utf-8")
    elif data_type == AssetType.TEXT:
        return data.encode("utf-8")
    else:
        raise TypeError(f"Unsupported data type {type(data)}")


def deserialize_asset(data: bytes, data_type: AssetType) -> Any:
    if data_type == AssetType.OBJECT:
        return cloudpickle.loads(data)
    elif data_type == AssetType.TRANSPORTABLE:
        return TransportableObject.deserialize(data)
    elif data_type == AssetType.JSONABLE:
        return json.loads(data.decode("utf-8"))
    elif data_type == AssetType.TEXT:
        return data.decode("utf-8")
    else:
        raise TypeError("Unsupported data type")


def _sha1_asset(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def save_asset(data: Any, data_type: AssetType, storage_path: str, filename: str) -> AssetSchema:
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
    scheme_prefix = "file://"
    uri = asset_meta.uri

    if not uri:
        return None

    if uri.startswith(scheme_prefix):
        path = uri[len(scheme_prefix) :]
    else:
        path = uri
    with open(path, "rb") as f:
        data = f.read()
    return deserialize_asset(data, data_type)
