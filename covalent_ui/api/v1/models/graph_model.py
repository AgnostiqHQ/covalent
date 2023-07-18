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

"""Graph request and response model"""

from datetime import datetime
from typing import Union

from pydantic import BaseModel


class GraphResponse(BaseModel):
    """Graph Response Model"""

    dispatch_id: Union[str, None] = None
    graph: Union[dict, None] = None


class GetDispatchLinks(BaseModel):
    edge_name: Union[str, None]
    parameter_type: Union[str, None]
    target: Union[int, None]
    source: Union[int, None]
    arg_index: Union[int, None]

    class Config:
        from_attributes = True


class GetDispatchNotes(BaseModel):
    id: int
    name: str
    node_id: int
    started_at: Union[datetime, None]
    completed_at: Union[datetime, None]
    status: Union[str, None]
    type: Union[str, None]
    executor_label: Union[str, None]
    sublattice_dispatch_id: Union[str, None]

    class Config:
        from_attributes = True
