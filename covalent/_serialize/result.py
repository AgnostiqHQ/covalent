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

"""Functions to convert lattice -> LatticeSchema"""


from .._results_manager.result import Result
from .._shared_files.schemas.lattice import LATTICE_ERROR_FILENAME, LATTICE_RESULTS_FILENAME
from .._shared_files.schemas.result import ResultAssets, ResultMetadata, ResultSchema
from .common import AssetType, load_asset, save_asset
from .lattice import deserialize_lattice, serialize_lattice

ASSET_TYPES = {
    "error": AssetType.TEXT,
    "result": AssetType.TRANSPORTABLE,
}


def _serialize_result_metadata(res: Result) -> ResultMetadata:
    return ResultMetadata(
        dispatch_id=res._dispatch_id,
        root_dispatch_id=res._root_dispatch_id,
        status=res._status,
    )


def _deserialize_result_metadata(meta: ResultMetadata) -> dict:
    return {
        "_dispatch_id": meta.dispatch_id,
        "_root_dispatch_id": meta.root_dispatch_id,
        "_status": meta.status,
    }


def _serialize_result_assets(res: Result, storage_path: str) -> ResultAssets:
    error_asset = save_asset(res._error, AssetType.TEXT, storage_path, LATTICE_ERROR_FILENAME)
    result_asset = save_asset(
        res._result, AssetType.TRANSPORTABLE, storage_path, LATTICE_RESULTS_FILENAME
    )
    return ResultAssets(result=result_asset, error=error_asset)


def _deserialize_result_assets(assets: ResultAssets) -> dict:
    error = load_asset(assets.error, AssetType.TEXT)
    result = load_asset(assets.result, AssetType.TRANSPORTABLE)
    return {
        "_result": result,
        "_error": error,
    }


def serialize_result(res: Result, storage_path: str) -> ResultSchema:
    meta = _serialize_result_metadata(res)
    assets = _serialize_result_assets(res, storage_path)
    lat = serialize_lattice(res.lattice, storage_path)
    return ResultSchema(metadata=meta, assets=assets, lattice=lat)


def deserialize_result(res: ResultSchema) -> Result:
    lat = deserialize_lattice(res.lattice)
    result_object = Result(lat)
    attrs = _deserialize_result_metadata(res.metadata)
    assets = _deserialize_result_assets(res.assets)

    attrs.update(assets)
    result_object.__dict__.update(attrs)
    return result_object
