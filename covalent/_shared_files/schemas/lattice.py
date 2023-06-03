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

"""FastAPI models for /api/v1/resultv2 endpoints"""


from pydantic import BaseModel

from .asset import AssetSchema
from .transport_graph import TransportGraphSchema

LATTICE_METADATA_KEYS = {
    "__name__",
    "python_version",
    "sdk_version",
    # metadata
    "executor",
    "workflow_executor",
    "executor_data",
    "workflow_executor_data",
}

LATTICE_ASSET_KEYS = {
    "workflow_function",
    "workflow_function_string",
    "__doc__",
    "inputs",
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
    # metadata
    "deps",
    "call_before",
    "call_after",
}

LATTICE_FUNCTION_FILENAME = "function.tobj"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_DOCSTRING_FILENAME = "function_docstring.txt"
LATTICE_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.tobj"
LATTICE_NAMED_ARGS_FILENAME = "named_args.tobj"
LATTICE_NAMED_KWARGS_FILENAME = "named_kwargs.tobj"
LATTICE_RESULTS_FILENAME = "results.tobj"
LATTICE_DEPS_FILENAME = "deps.json"
LATTICE_CALL_BEFORE_FILENAME = "call_before.json"
LATTICE_CALL_AFTER_FILENAME = "call_after.json"
LATTICE_COVA_IMPORTS_FILENAME = "cova_imports.pkl"
LATTICE_LATTICE_IMPORTS_FILENAME = "lattice_imports.pkl"
LATTICE_STORAGE_TYPE = "file"


ASSET_FILENAME_MAP = {
    "workflow_function": LATTICE_FUNCTION_FILENAME,
    "workflow_function_string": LATTICE_FUNCTION_STRING_FILENAME,
    "doc": LATTICE_DOCSTRING_FILENAME,
    "inputs": LATTICE_INPUTS_FILENAME,
    "named_args": LATTICE_NAMED_ARGS_FILENAME,
    "named_kwargs": LATTICE_NAMED_KWARGS_FILENAME,
    "cova_imports": LATTICE_COVA_IMPORTS_FILENAME,
    "lattice_imports": LATTICE_LATTICE_IMPORTS_FILENAME,
    "deps": LATTICE_DEPS_FILENAME,
    "call_before": LATTICE_CALL_BEFORE_FILENAME,
    "call_after": LATTICE_CALL_AFTER_FILENAME,
}


class LatticeAssets(BaseModel):
    workflow_function: AssetSchema
    workflow_function_string: AssetSchema
    doc: AssetSchema  # __doc__
    inputs: AssetSchema
    named_args: AssetSchema
    named_kwargs: AssetSchema
    cova_imports: AssetSchema
    lattice_imports: AssetSchema

    # lattice.metadata
    deps: AssetSchema
    call_before: AssetSchema
    call_after: AssetSchema


class LatticeMetadata(BaseModel):
    name: str  # __name__
    executor: str
    executor_data: dict
    workflow_executor: str
    workflow_executor_data: dict
    python_version: str
    sdk_version: str


class LatticeSchema(BaseModel):
    metadata: LatticeMetadata
    assets: LatticeAssets
    transport_graph: TransportGraphSchema
