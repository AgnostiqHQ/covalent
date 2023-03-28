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
    "named_args",
    "named_kwargs",
    "cova_imports",
    "lattice_imports",
    # metadata
    "deps",
    "call_before",
    "call_after",
}


class LatticeAssets(BaseModel):
    workflow_function: AssetSchema
    workflow_function_string: AssetSchema
    doc: AssetSchema  # __doc__
    named_args: AssetSchema
    named_kwargs: AssetSchema
    cova_imports: AssetSchema
    lattice_imports: AssetSchema

    inputs: AssetSchema

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


class LatticeSchema(BaseModel):
    metadata: LatticeMetadata
    assets: LatticeAssets
    transport_graph: TransportGraphSchema
