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


from datetime import datetime
from typing import Any, Optional, Sequence

from pydantic import BaseModel


class BaseNode(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    status: str
    output: Any
    error: Optional[str]
    stdout: str
    stderr: str


class Link(BaseModel):
    edge_name: str
    param_type: str
    source: int
    target: int


class Node(BaseNode):
    id: int


class Graph(BaseModel):
    nodes: Sequence[Node]
    links: Sequence[Link]


class Result(BaseModel):
    dispatch_id: str
    results_dir: str
    status: str
    graph: Graph


class InsertResultResponse(BaseModel):
    dispatch_id: str


class UpdateResultResponse(BaseModel):
    response: str


class ResultPickle(BaseModel):
    result_object: bytes
