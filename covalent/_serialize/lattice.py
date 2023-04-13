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

from .._shared_files.schemas.lattice import (
    ASSET_FILENAME_MAP,
    LatticeAssets,
    LatticeMetadata,
    LatticeSchema,
)
from .._workflow.lattice import Lattice
from .common import AssetType, load_asset, save_asset
from .transport_graph import deserialize_transport_graph, serialize_transport_graph

ASSET_TYPES = {
    "workflow_function": AssetType.TRANSPORTABLE,
    "workflow_function_string": AssetType.TEXT,
    "doc": AssetType.TEXT,
    "named_args": AssetType.OBJECT,
    "named_kwargs": AssetType.OBJECT,
    "cova_imports": AssetType.OBJECT,
    "lattice_imports": AssetType.OBJECT,
    "deps": AssetType.OBJECT,
    "call_before": AssetType.OBJECT,
    "call_after": AssetType.OBJECT,
}


def _serialize_lattice_metadata(lat) -> LatticeMetadata:
    name = lat.__name__
    executor = lat.metadata["executor"]
    executor_data = lat.metadata["executor_data"]
    workflow_executor = lat.metadata["workflow_executor"]
    workflow_executor_data = lat.metadata["workflow_executor_data"]
    return LatticeMetadata(
        name=name,
        executor=executor,
        executor_data=executor_data,
        workflow_executor=workflow_executor,
        workflow_executor_data=workflow_executor_data,
    )


def _deserialize_lattice_metadata(meta: LatticeMetadata) -> dict:
    return {
        "__name__": meta.name,
        "metadata": {
            "executor": meta.executor,
            "executor_data": meta.executor_data,
            "workflow_executor": meta.workflow_executor,
            "workflow_executor_data": meta.workflow_executor_data,
        },
    }


def _serialize_lattice_assets(lat, storage_path: str) -> LatticeAssets:
    workflow_func_asset = save_asset(
        lat.workflow_function,
        ASSET_TYPES["workflow_function"],
        storage_path,
        ASSET_FILENAME_MAP["workflow_function"],
    )

    try:
        workflow_func_string = lat.workflow_function_string
    except AttributeError:
        workflow_func_string = ""
    workflow_func_str_asset = save_asset(
        workflow_func_string,
        ASSET_TYPES["workflow_function_string"],
        storage_path,
        ASSET_FILENAME_MAP["workflow_function_string"],
    )

    docstring = "" if lat.__doc__ is None else lat.__doc__
    docstring_asset = save_asset(
        docstring,
        ASSET_TYPES["doc"],
        storage_path,
        ASSET_FILENAME_MAP["doc"],
    )

    # Deprecate
    named_args_asset = save_asset(
        lat.named_args,
        ASSET_TYPES["named_args"],
        storage_path,
        ASSET_FILENAME_MAP["named_args"],
    )
    named_kwargs_asset = save_asset(
        lat.named_kwargs,
        ASSET_TYPES["named_kwargs"],
        storage_path,
        ASSET_FILENAME_MAP["named_kwargs"],
    )
    cova_imports_asset = save_asset(
        lat.cova_imports,
        ASSET_TYPES["cova_imports"],
        storage_path,
        ASSET_FILENAME_MAP["cova_imports"],
    )
    lattice_imports_asset = save_asset(
        lat.lattice_imports,
        ASSET_TYPES["lattice_imports"],
        storage_path,
        ASSET_FILENAME_MAP["lattice_imports"],
    )

    # NOTE: these are actually JSONable
    deps_asset = save_asset(
        lat.metadata["deps"],
        ASSET_TYPES["deps"],
        storage_path,
        ASSET_FILENAME_MAP["deps"],
    )
    call_before_asset = save_asset(
        lat.metadata["call_before"],
        ASSET_TYPES["call_before"],
        storage_path,
        ASSET_FILENAME_MAP["call_before"],
    )
    call_after_asset = save_asset(
        lat.metadata["call_after"],
        ASSET_TYPES["call_after"],
        storage_path,
        ASSET_FILENAME_MAP["call_after"],
    )

    return LatticeAssets(
        workflow_function=workflow_func_asset,
        workflow_function_string=workflow_func_str_asset,
        doc=docstring_asset,
        named_args=named_args_asset,
        named_kwargs=named_kwargs_asset,
        cova_imports=cova_imports_asset,
        lattice_imports=lattice_imports_asset,
        deps=deps_asset,
        call_before=call_before_asset,
        call_after=call_after_asset,
    )


def _deserialize_lattice_assets(assets: LatticeAssets) -> dict:
    workflow_function = load_asset(assets.workflow_function, AssetType.TRANSPORTABLE)
    workflow_function_string = load_asset(assets.workflow_function_string, AssetType.TEXT)
    doc = load_asset(assets.doc, AssetType.TEXT)
    named_args = load_asset(assets.named_args, AssetType.OBJECT)
    named_kwargs = load_asset(assets.named_kwargs, AssetType.OBJECT)
    cova_imports = load_asset(assets.cova_imports, AssetType.OBJECT)
    lattice_imports = load_asset(assets.lattice_imports, AssetType.OBJECT)
    deps = load_asset(assets.deps, AssetType.OBJECT)
    call_before = load_asset(assets.call_before, AssetType.OBJECT)
    call_after = load_asset(assets.call_after, AssetType.OBJECT)
    return {
        "workflow_function": workflow_function,
        "workflow_function_string": workflow_function_string,
        "__doc__": doc,
        "named_args": named_args,
        "named_kwargs": named_kwargs,
        "cova_imports": cova_imports,
        "lattice_imports": lattice_imports,
        "metadata": {
            "deps": deps,
            "call_before": call_before,
            "call_after": call_after,
        },
    }


def serialize_lattice(lat, storage_path: str) -> LatticeSchema:
    meta = _serialize_lattice_metadata(lat)
    assets = _serialize_lattice_assets(lat, storage_path)

    tg = serialize_transport_graph(lat.transport_graph, storage_path)

    return LatticeSchema(metadata=meta, assets=assets, transport_graph=tg)


def deserialize_lattice(model: LatticeSchema) -> Lattice:
    def dummy_function(x):
        return x

    lat = Lattice(dummy_function)

    attrs = _deserialize_lattice_metadata(model.metadata)
    assets = _deserialize_lattice_assets(model.assets)

    metadata = assets.pop("metadata")
    attrs.update(assets)
    attrs["metadata"].update(metadata)

    tg = deserialize_transport_graph(model.transport_graph)

    attrs["transport_graph"] = tg

    lat.__dict__.update(attrs)

    if lat.named_args:
        lat.args = [v for _, v in lat.named_args.items()]
    if lat.named_kwargs:
        lat.kwargs = lat.named_kwargs

    return lat
