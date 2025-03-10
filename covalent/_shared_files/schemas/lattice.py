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

from pydantic import BaseModel

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
    # user dependent assets
    "hooks",
}

LATTICE_FUNCTION_FILENAME = "function.tobj"
LATTICE_FUNCTION_STRING_FILENAME = "function_string.txt"
LATTICE_DOCSTRING_FILENAME = "function_docstring.txt"
LATTICE_EXECUTOR_DATA_FILENAME = "executor_data.pkl"
LATTICE_WORKFLOW_EXECUTOR_DATA_FILENAME = "workflow_executor_data.pkl"
LATTICE_ERROR_FILENAME = "error.log"
LATTICE_INPUTS_FILENAME = "inputs.tobj"
LATTICE_RESULTS_FILENAME = "results.tobj"
LATTICE_HOOKS_FILENAME = "hooks.json"
LATTICE_CALL_BEFORE_FILENAME = "call_before.json"
LATTICE_CALL_AFTER_FILENAME = "call_after.json"
LATTICE_STORAGE_TYPE = "file"


ASSET_FILENAME_MAP = {
    "workflow_function": LATTICE_FUNCTION_FILENAME,
    "workflow_function_string": LATTICE_FUNCTION_STRING_FILENAME,
    "doc": LATTICE_DOCSTRING_FILENAME,
    "inputs": LATTICE_INPUTS_FILENAME,
    "hooks": LATTICE_HOOKS_FILENAME,
}


class LatticeAssets(BaseModel):
    workflow_function: AssetSchema
    workflow_function_string: AssetSchema
    doc: AssetSchema  # __doc__
    inputs: AssetSchema

    # lattice.metadata
    hooks: AssetSchema

    _custom: Optional[Dict[str, AssetSchema]] = None


class LatticeMetadata(BaseModel):
    name: str  # __name__
    executor: str
    executor_data: dict
    workflow_executor: str
    workflow_executor_data: dict
    python_version: Optional[str] = None
    covalent_version: Optional[str] = None

    _custom: Optional[Dict] = None


class LatticeSchema(BaseModel):
    metadata: LatticeMetadata
    assets: LatticeAssets

    transport_graph: TransportGraphSchema
