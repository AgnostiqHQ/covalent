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

from .._shared_files.schemas.lattice import LatticeAssets, LatticeMetadata, LatticeSchema
from .serializers import AssetType, save_asset
from .transport_graph import serialize_transport_graph

LATTICE_FUNCTION_FILENAME = "function.pkl"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_DOCSTRING_FILENAME = "function_docstring.txt"
LATTICE_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.pkl"
LATTICE_NAMED_ARGS_FILENAME = "named_args.pkl"
LATTICE_NAMED_KWARGS_FILENAME = "named_kwargs.pkl"
LATTICE_RESULTS_FILENAME = "results.pkl"
LATTICE_DEPS_FILENAME = "deps.pkl"
LATTICE_CALL_BEFORE_FILENAME = "call_before.pkl"
LATTICE_CALL_AFTER_FILENAME = "call_after.pkl"
LATTICE_COVA_IMPORTS_FILENAME = "cova_imports.pkl"
LATTICE_LATTICE_IMPORTS_FILENAME = "lattice_imports.pkl"
LATTICE_STORAGE_TYPE = "file"


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


def _serialize_lattice_assets(lat, storage_path) -> LatticeAssets:
    workflow_func_asset = save_asset(
        lat.workflow_function, AssetType.TRANSPORTABLE, storage_path, LATTICE_FUNCTION_FILENAME
    )

    try:
        workflow_func_string = lat.workflow_function_string
    except AttributeError:
        workflow_func_string = ""
    workflow_func_str_asset = save_asset(
        workflow_func_string, AssetType.TEXT, storage_path, LATTICE_FUNCTION_STRING_FILENAME
    )

    docstring = "" if lat.__doc__ is None else lat.__doc__
    docstring_asset = save_asset(
        docstring, AssetType.TEXT, storage_path, LATTICE_DOCSTRING_FILENAME
    )

    # Deprecate
    named_args_asset = save_asset(
        lat.named_args, AssetType.OBJECT, storage_path, LATTICE_NAMED_ARGS_FILENAME
    )
    named_kwargs_asset = save_asset(
        lat.named_kwargs, AssetType.OBJECT, storage_path, LATTICE_NAMED_KWARGS_FILENAME
    )
    cova_imports_asset = save_asset(
        lat.cova_imports, AssetType.OBJECT, storage_path, LATTICE_COVA_IMPORTS_FILENAME
    )
    lattice_imports_asset = save_asset(
        lat.lattice_imports, AssetType.OBJECT, storage_path, LATTICE_LATTICE_IMPORTS_FILENAME
    )

    # NOTE: these are actually JSONable
    deps_asset = save_asset(
        lat.metadata["deps"], AssetType.OBJECT, storage_path, LATTICE_DEPS_FILENAME
    )
    call_before_asset = save_asset(
        lat.metadata["call_before"], AssetType.OBJECT, storage_path, LATTICE_CALL_BEFORE_FILENAME
    )
    call_after_asset = save_asset(
        lat.metadata["call_after"], AssetType.OBJECT, storage_path, LATTICE_CALL_AFTER_FILENAME
    )

    # NOTE: We can avoid pickling here since the UI actually consumes only the string representation
    inputs = {}
    inputs["args"] = lat.args if lat.args else []
    inputs["kwargs"] = lat.kwargs if lat.kwargs else {}

    inputs_asset = save_asset(inputs, AssetType.OBJECT, storage_path, LATTICE_INPUTS_FILENAME)

    return LatticeAssets(
        workflow_function=workflow_func_asset,
        workflow_function_string=workflow_func_str_asset,
        doc=docstring_asset,
        named_args=named_args_asset,
        named_kwargs=named_kwargs_asset,
        cova_imports=cova_imports_asset,
        lattice_imports=lattice_imports_asset,
        inputs=inputs_asset,
        deps=deps_asset,
        call_before=call_before_asset,
        call_after=call_after_asset,
    )


def serialize_lattice(lat, storage_path) -> LatticeSchema:
    meta = _serialize_lattice_metadata(lat)
    assets = _serialize_lattice_assets(lat, storage_path)

    tg = serialize_transport_graph(lat.transport_graph, storage_path)

    return LatticeSchema(metadata=meta, assets=assets, transport_graph=tg)
