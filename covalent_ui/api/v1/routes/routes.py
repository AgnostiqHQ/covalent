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

"""Routes"""

from fastapi import APIRouter

from covalent_dispatcher._service import app, assets, runnersvc
from covalent_dispatcher._triggers_app.app import router as tr_router
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
routes.include_router(tr_router, prefix="/api", tags=["Triggers"])
routes.include_router(app.router, prefix="/api/v2", tags=["Dispatcher"])
routes.include_router(assets.router, prefix="/api/v2", tags=["Assets"])
routes.include_router(runnersvc.router, prefix="/api/v2", tags=["Runner"])
