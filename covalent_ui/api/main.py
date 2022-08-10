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

"""Fastapi init"""

import socketio
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent_ui.api.v1.routes import routes

# Config

WEBHOOK_PATH = "/api/webhook"
address = get_config("user_interface.address")
port = str(get_config("user_interface.dev_port"))
socket_port = str(get_config("user_interface.port"))
origins = [f"http://{address}:{port}"]
socket_origins = [f"http://{address}:{port}", f"http://{address}:{socket_port}"]

app_log = logger.app_log

app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins=socket_origins, async_mode="asgi")


@sio.on("message")
async def chat_message(sid, data):
    await sio.emit("draw-request", "hi ")


app.include_router(routes.routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.detail}),
    )


@app.post(WEBHOOK_PATH)
async def handle_result_update(result_update: dict):
    await sio.emit("result-update", result_update)
    return {"ok": True}


@app.post("/api/draw")
async def handle_draw_request(draw_request: dict):
    await sio.emit("draw_request", draw_request)
    return {"ok": True}
