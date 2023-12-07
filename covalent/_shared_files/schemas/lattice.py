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

"""FastAPI models for /api/v1/resultv2 endpoints"""

from typing import Dict, Optional

from pydantic import BaseModel, field_validator

from .asset import AssetSchema
from .transport_graph import TransportGraphSchema

LATTICE_METADATA_KEYS = {
    "__name__",
    "python_version",
    "covalent_version",
    # user dependent metadata
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
    # user dependent assets
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
LATTICE_COVA_IMPORTS_FILENAME = "cova_imports.json"
LATTICE_LATTICE_IMPORTS_FILENAME = "lattice_imports.txt"
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
    covalent_version: str


class LatticeSchema(BaseModel):
    metadata: LatticeMetadata
    assets: LatticeAssets
    custom_assets: Optional[Dict[str, AssetSchema]] = None

    transport_graph: TransportGraphSchema

    @field_validator("custom_assets")
    def check_custom_asset_keys(cls, v):
        if v is not None:
            for key in v:
                if key in ASSET_FILENAME_MAP:
                    raise ValueError(f"Asset {key} conflicts with built-in key")
        return v
