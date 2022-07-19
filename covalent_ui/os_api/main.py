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
import argparse
import os

import socketio
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from covalent._shared_files.config import get_config
from covalent_ui.os_api.api_v0.routes import routes

app = FastAPI()
user = os.getlogin()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = []
    errors = exc.errors()
    for d in errors:
        message.append(d["msg"])
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"errors": message}),
    )


@app.on_event("startup")
async def app_init():
    """app init"""
    app.include_router(routes.routes, prefix="/api/v1")


# socket


sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
socketio_app = socketio.ASGIApp(sio, app)


@sio.event
def connect():
    print("connect ")


@sio.on("message")
async def chat_message(data):
    print("message ", data)
    await sio.emit("response", "hi " + data)


@sio.event
def disconnect():
    print("disconnect ")


@app.post("/api/draw")
async def handle_result_update(result_update):
    await sio.emit("result-update", result_update)
    return {{"ok": True}}


@app.post("/api/draw")
async def handle_draw_request(draw_request):
    await sio.emit("draw_request", draw_request)
    return {{"ok": True}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("-p", "--port", required=False, help="Server port number.")
    ap.add_argument(
        "-d",
        "--develop",
        required=False,
        action="store_true",
        help="Start the server in developer mode.",
    )
    # ap.add_argument("--no-cluster", required=False, help="Start Covalent server without Dask")

    args, unknown = ap.parse_known_args()

    # port to be specified by cli
    if args.port:
        PORT = int(args.port)
    else:
        PORT = int(get_config("dispatcher.port"))

    DEBUG = True if args.develop is True else False
    # reload = True if args.develop is True else False
    RELOAD = True

    uvicorn.run("main:app", debug=DEBUG, host="0.0.0.0", reload=RELOAD, port=8000)
