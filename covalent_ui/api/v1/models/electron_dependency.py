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
# Relief from the License may be granted by purchasing a commercial license.

"""Electron Dependency Request and Respone Model"""

from typing import List

from pydantic import BaseModel

from covalent_ui.api.v1.utils.status import Status


class LinkModule(BaseModel):
    """Link Module Validation"""

    id: int
    electron_id: int
    parent_electron_id: int
    edge_name: str
    parameter_type: str
    created_at: str


class NodeModule(BaseModel):
    """Node Module Validation"""

    id: int
    name: str
    start_time: str
    end_time: str
    status: Status


class GraphResponseModel(BaseModel):
    """Graph Response Validation"""

    node: List[NodeModule]
    links: List[LinkModule]
