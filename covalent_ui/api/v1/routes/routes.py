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

"""Routes"""

from fastapi import APIRouter

from covalent_dispatcher._service import app
from covalent_ui.api.v1.routes.end_points import (
    electron_routes,
    graph_route,
    lattice_route,
    logs_route,
    settings_routes,
    summary_routes,
)

routes = APIRouter()

dispatch_prefix = "/api/v1/dispatches"

routes.include_router(summary_routes.routes, prefix=dispatch_prefix, tags=["Dispatches"])
routes.include_router(lattice_route.routes, prefix=dispatch_prefix, tags=["Dispatches"])
routes.include_router(graph_route.routes, prefix=dispatch_prefix, tags=["Graph"])
routes.include_router(electron_routes.routes, prefix=dispatch_prefix, tags=["Electrons"])
routes.include_router(settings_routes.routes, prefix="/api/v1", tags=["Settings"])
routes.include_router(logs_route.routes, prefix="/api/v1/logs", tags=["Logs"])
routes.include_router(app.router, prefix="/api", tags=["dispatcher"])
routes.include_router(app.router, prefix="/api", tags=["dispatcher"])
