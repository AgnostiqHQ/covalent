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

import logging
import os
from pathlib import Path

from app.api.api_v0.api import api_router
from app.core.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_socketio import SocketManager
from starlette.exceptions import HTTPException

BASE_PATH = Path(__file__).resolve().parent
FRONTEND_PATH = "/webapp/build"


class SinglePageApp(StaticFiles):
    """
    Allow URL paths (e.g. /preview or /[dispatch_id]) to be handled by the web
    app by overriding the handling of 404 exceptions and passing control to the
    app instead (/index.html)
    """

    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
        except HTTPException as e:
            if e.status_code == 404:
                # return /index.html
                response = await super().get_response(".", scope)
        return response


app = FastAPI(title="Covalent UI Backend Service API")

sio = SocketManager(app=app)

logging.basicConfig(level=logging.DEBUG)

app.include_router(api_router, prefix=settings.API_V0_STR)

app.mount("/", SinglePageApp(directory=f"{BASE_PATH}{FRONTEND_PATH}", html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.UI_SVC_HOST,
        port=settings.UI_SVC_PORT,
        log_level="debug",
        reload=False,
    )
