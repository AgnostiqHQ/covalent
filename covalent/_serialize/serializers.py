import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any

import cloudpickle

from .._shared_files.schemas.asset import AssetSchema


class AssetType(Enum):
    OBJECT = 0
    TRANSPORTABLE = 1
    JSONABLE = 2
    TEXT = 3


def _serialize_asset(data: Any, data_type: AssetType) -> bytes:
    if data_type == AssetType.OBJECT:
        return cloudpickle.dumps(data)
    elif data_type == AssetType.TRANSPORTABLE:
        return cloudpickle.dumps(data)
    elif data_type == AssetType.JSONABLE:
        return json.dumps(data)
    else:
        if not isinstance(data, str):
            raise TypeError(f"Unsupported data type {type(data)}")
        else:
            return data.encode("utf-8")


def _sha1_asset(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def save_asset(data: Any, data_type: AssetType, storage_path: str, filename: str) -> AssetSchema:
    scheme = "file"

    serialized = _serialize_asset(data, data_type)
    digest = _sha1_asset(serialized)
    path = Path(storage_path) / filename
    path = path.resolve()
    with open(path, "wb") as f:
        f.write(serialized)
    uri = f"{scheme}://{path}"
    return AssetSchema(digest=digest, uri=uri)
