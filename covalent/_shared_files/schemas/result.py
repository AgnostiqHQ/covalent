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

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .asset import AssetSchema
from .lattice import LatticeSchema

METADATA_KEYS = {
    "start_time",
    "end_time",
    "dispatch_id",
    "root_dispatch_id",
    "status",
    "num_nodes",
}


ASSET_KEYS = {
    "inputs",
    "result",
    "error",
}


class ResultMetadata(BaseModel):
    dispatch_id: str
    root_dispatch_id: str
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]


class ResultAssets(BaseModel):
    inputs: AssetSchema
    result: AssetSchema
    error: AssetSchema


class ResultSchema(BaseModel):
    metadata: ResultMetadata
    assets: ResultAssets
    lattice: LatticeSchema
