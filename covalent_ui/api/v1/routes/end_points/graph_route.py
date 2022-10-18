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

"""Graph Route"""

import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from covalent_ui.api.v1.data_layer.graph_dal import Graph
from covalent_ui.api.v1.database.config.db import engine
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

    with Session(engine) as session:

        graph = Graph(session)
        graph_data = graph.get_graph(dispatch_id)
        if graph_data is not None:
            return GraphResponse(
                dispatch_id=graph_data["dispatch_id"],
                graph={"nodes": graph_data["nodes"], "links": graph_data["links"]},
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
