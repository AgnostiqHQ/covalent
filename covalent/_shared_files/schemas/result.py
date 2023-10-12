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

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .asset import AssetSchema
from .common import StatusEnum
from .lattice import LATTICE_ERROR_FILENAME, LATTICE_RESULTS_FILENAME, LatticeSchema

METADATA_KEYS = {
    "start_time",
    "end_time",
    "dispatch_id",
    "root_dispatch_id",
    "status",
    "num_nodes",
}


ASSET_KEYS = {
    "result",
    "error",
}


ASSET_FILENAME_MAP = {
    "result": LATTICE_RESULTS_FILENAME,
    "error": LATTICE_ERROR_FILENAME,
}


class ResultMetadata(BaseModel):
    dispatch_id: str
    root_dispatch_id: str
    status: StatusEnum
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # For use by redispatch
    def reset(self):
        self.dispatch_id = ""
        self.root_dispatch_id = ""
        self.status = StatusEnum.NEW_OBJECT
        self.start_time = None
        self.end_time = None


class ResultAssets(BaseModel):
    result: AssetSchema
    error: AssetSchema


class ResultSchema(BaseModel):
    metadata: ResultMetadata
    assets: ResultAssets
    lattice: LatticeSchema

    # For use by redispatch
    def reset_metadata(self):
        self.metadata.reset()

        tg = self.lattice.transport_graph
        for node in tg.nodes:
            node.metadata.reset()
