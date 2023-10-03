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

from typing import List

from pydantic import BaseModel

from .edge import EdgeSchema
from .electron import ElectronSchema


class TransportGraphSchema(BaseModel):
    nodes: List[ElectronSchema]
    links: List[EdgeSchema]

    # For use by redispatch
    def reset(self):
        for node in self.nodes:
            node.metadata.reset()
