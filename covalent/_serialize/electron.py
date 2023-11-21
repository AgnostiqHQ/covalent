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

"""Functions to convert node -> ElectronSchema"""

from typing import Dict

from .._shared_files.schemas.electron import (
    ASSET_FILENAME_MAP,
    AssetSchema,
    ElectronAssets,
    ElectronMetadata,
    ElectronSchema,
)
from .._shared_files.util_classes import RESULT_STATUS, Status
from .._workflow.transportable_object import TransportableObject
from .common import AssetType, load_asset, save_asset

__all__ = [
    "serialize_node",
    "deserialize_node",
]


ASSET_TYPES = {
    "function": AssetType.TRANSPORTABLE,
    "function_string": AssetType.TEXT,
    "value": AssetType.TRANSPORTABLE,
    "output": AssetType.TRANSPORTABLE,
    "deps": AssetType.JSONABLE,
    "call_before": AssetType.JSONABLE,
    "call_after": AssetType.JSONABLE,
    "qelectron_db": AssetType.BYTES,
    "stdout": AssetType.TEXT,
    "stderr": AssetType.TEXT,
    "error": AssetType.TEXT,
}


def _serialize_node_metadata(node_attrs: dict, node_storage_path: str) -> ElectronMetadata:
    task_group_id = node_attrs["task_group_id"]
    name = node_attrs["name"]
    executor = node_attrs["metadata"]["executor"]
    executor_data = node_attrs["metadata"]["executor_data"]
    qelectron_data_exists = node_attrs["metadata"]["qelectron_data_exists"]

    # Optional
    status = node_attrs.get("status", RESULT_STATUS.NEW_OBJECT)

    start_time = node_attrs.get("start_time")
    if start_time:
        start_time = start_time.isoformat()

    end_time = node_attrs.get("end_time")
    if end_time:
        end_time = end_time.isoformat()

    return ElectronMetadata(
        task_group_id=task_group_id,
        name=name,
        executor=executor,
        executor_data=executor_data,
        qelectron_data_exists=qelectron_data_exists,
        status=str(status),
        start_time=start_time,
        end_time=end_time,
    )


def _deserialize_node_metadata(meta: ElectronMetadata) -> dict:
    return {
        "task_group_id": meta.task_group_id,
        "name": meta.name,
        "status": Status(meta.status),
        "start_time": meta.start_time,
        "end_time": meta.end_time,
        "sub_dispatch_id": meta.sub_dispatch_id,
        "metadata": {
            "executor": meta.executor,
            "executor_data": meta.executor_data,
            "qelectron_data_exists": meta.qelectron_data_exists,
        },
    }


def _serialize_node_assets(node_attrs: dict, node_storage_path: str) -> ElectronAssets:
    function = node_attrs["function"]
    function_asset = save_asset(
        function,
        ASSET_TYPES["function"],
        node_storage_path,
        ASSET_FILENAME_MAP["function"],
    )

    function_string = node_attrs.get("function_string", "")
    function_string_asset = save_asset(
        function_string,
        ASSET_TYPES["function_string"],
        node_storage_path,
        ASSET_FILENAME_MAP["function_string"],
    )

    node_value = node_attrs.get("value", TransportableObject(None))
    value_asset = save_asset(
        node_value,
        ASSET_TYPES["value"],
        node_storage_path,
        ASSET_FILENAME_MAP["value"],
    )

    node_output = node_attrs.get("output", TransportableObject(None))
    output_asset = save_asset(
        node_output,
        ASSET_TYPES["output"],
        node_storage_path,
        ASSET_FILENAME_MAP["output"],
    )

    node_stdout = node_attrs.get("stdout", "")
    stdout_asset = save_asset(
        node_stdout,
        ASSET_TYPES["stdout"],
        node_storage_path,
        ASSET_FILENAME_MAP["stdout"],
    )

    node_stderr = node_attrs.get("stderr", "")
    stderr_asset = save_asset(
        node_stderr,
        ASSET_TYPES["stderr"],
        node_storage_path,
        ASSET_FILENAME_MAP["stderr"],
    )

    qelectron_db = node_attrs.get("qelectron_db", bytes())
    qelectron_db_asset = save_asset(
        qelectron_db,
        ASSET_TYPES["qelectron_db"],
        node_storage_path,
        ASSET_FILENAME_MAP["qelectron_db"],
    )

    node_error = node_attrs.get("error", "")
    error_asset = save_asset(
        node_error,
        ASSET_TYPES["error"],
        node_storage_path,
        ASSET_FILENAME_MAP["error"],
    )

    deps = node_attrs["metadata"]["deps"]
    deps_asset = save_asset(
        deps, ASSET_TYPES["deps"], node_storage_path, ASSET_FILENAME_MAP["deps"]
    )

    call_before = node_attrs["metadata"]["call_before"]
    call_before_asset = save_asset(
        call_before,
        ASSET_TYPES["call_before"],
        node_storage_path,
        ASSET_FILENAME_MAP["call_before"],
    )

    call_after = node_attrs["metadata"]["call_after"]
    call_after_asset = save_asset(
        call_after,
        ASSET_TYPES["call_after"],
        node_storage_path,
        ASSET_FILENAME_MAP["call_after"],
    )

    return ElectronAssets(
        function=function_asset,
        function_string=function_string_asset,
        value=value_asset,
        output=output_asset,
        stdout=stdout_asset,
        stderr=stderr_asset,
        qelectron_db=qelectron_db_asset,
        error=error_asset,
        deps=deps_asset,
        call_before=call_before_asset,
        call_after=call_after_asset,
    )


def _deserialize_node_assets(ea: ElectronAssets) -> dict:
    function = load_asset(ea.function, ASSET_TYPES["function"])
    function_string = load_asset(ea.function_string, ASSET_TYPES["function_string"])
    value = load_asset(ea.value, ASSET_TYPES["value"])
    output = load_asset(ea.output, ASSET_TYPES["output"])
    stdout = load_asset(ea.stdout, ASSET_TYPES["stdout"])
    stderr = load_asset(ea.stderr, ASSET_TYPES["stderr"])
    qelectron_db = load_asset(ea.qelectron_db, ASSET_TYPES["qelectron_db"])
    error = load_asset(ea.error, ASSET_TYPES["error"])

    deps = load_asset(ea.deps, ASSET_TYPES["deps"])
    call_before = load_asset(ea.call_before, ASSET_TYPES["call_before"])
    call_after = load_asset(ea.call_after, ASSET_TYPES["call_after"])

    return {
        "function": function,
        "function_string": function_string,
        "value": value,
        "output": output,
        "stdout": stdout,
        "stderr": stderr,
        "qelectron_db": qelectron_db,
        "error": error,
        "metadata": {
            "deps": deps,
            "call_before": call_before,
            "call_after": call_after,
        },
    }


def _get_node_custom_assets(node_attrs: dict) -> Dict[str, AssetSchema]:
    if "custom_asset_keys" in node_attrs["metadata"]:
        return {key: AssetSchema() for key in node_attrs["metadata"]["custom_asset_keys"]}


def serialize_node(node_id: int, node_attrs: dict, node_storage_path) -> ElectronSchema:
    meta = _serialize_node_metadata(node_attrs, node_storage_path)
    assets = _serialize_node_assets(node_attrs, node_storage_path)
    custom_assets = _get_node_custom_assets(node_attrs)
    return ElectronSchema(id=node_id, metadata=meta, assets=assets, custom_assets=custom_assets)


def deserialize_node(e: ElectronSchema, metadata_only: bool = False) -> dict:
    node_attrs = _deserialize_node_metadata(e.metadata)
    node_assets = _deserialize_node_assets(e.assets)

    asset_metadata = node_assets.pop("metadata")

    if not metadata_only:
        node_attrs.update(node_assets)

    # merge "metadata" attrs
    node_attrs["metadata"].update(asset_metadata)

    return {"id": e.id, "attrs": node_attrs}
