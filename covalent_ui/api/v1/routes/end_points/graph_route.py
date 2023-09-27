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

"""Graph Route"""

import uuid

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import covalent_ui.api.v1.database.config.db as db
from covalent_ui.api.v1.data_layer.graph_dal import Graph
from covalent_ui.api.v1.models.graph_model import GraphResponse

routes: APIRouter = APIRouter()


@routes.get("/{dispatch_id}/graph", response_model=GraphResponse)
def get_graph(dispatch_id: uuid.UUID):
    """Get Graph

    Args:
        dispatch_id: To fetch lattice data with the provided dispatch id

    Returns:
        Returns the lattice data with the dispatch id provided
    """

    with Session(db.engine) as session:
        graph = Graph(session)
        graph_data = graph.get_graph(dispatch_id)
        if graph_data is not None:
            return GraphResponse(
                dispatch_id=graph_data["dispatch_id"],
                graph={
                    "nodes": jsonable_encoder(graph_data["nodes"]),
                    "links": jsonable_encoder(graph_data["links"]),
                },
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[
                {
                    "loc": ["path", "dispatch_id"],
                    "msg": f"Dispatch ID {dispatch_id} does not exist",
                    "type": None,
                }
            ],
        )
