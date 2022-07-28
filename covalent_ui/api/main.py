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
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent_dispatcher._service.app_dask import DaskCluster

# from covalent_ui.app import app as flask_app
from covalent_ui.api.v1.routes import routes

WEBHOOK_PATH = "/api/webhook"
WEBAPP_PATH = "../webapp/build"
ROUTE_WEBAPP_PATH = "/webapp/build"

app_log = logger.app_log

app = FastAPI()
user = os.getlogin()

sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode="asgi")
# socketio_app = socketio.ASGIApp(sio, app)


@sio.event
def connect(sid, environ):
    print("connect ", sid)


@sio.on("message")
async def chat_message(sid, data):
    print("message ", data)
    await sio.emit("draw-request", "hi ")


@sio.event
def disconnect(sid):
    print("disconnect ", sid)


# app.mount(ROUTE_WEBAPP_PATH, StaticFiles(directory=WEBAPP_PATH), name="webapp")
origins = ["http://localhost:49009", "http://localhost:48008"]
app.include_router(routes.routes, prefix="/api/v1")

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


# app.mount("/", WSGIMiddleware(flask_app))

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
    ap.add_argument("--no-cluster", required=False, help="Start Covalent server without Dask")

    args, unknown = ap.parse_known_args()

    # port to be specified by cli
    if args.port:
        PORT = int(args.port)
    else:
        PORT = int(get_config("dispatcher.port"))

    DEBUG = True if args.develop is True else False
    # reload = True if args.develop is True else False
    RELOAD = True

    # Start dask if no-cluster flag is not specified (covalent stop auto terminates all child processes of this)
    if not args.no_cluster:
        dask_cluster = DaskCluster(name="LocalDaskCluster", logger=app_log)
        dask_cluster.start()

    uvicorn.run("main:socketio_app", debug=DEBUG, host="0.0.0.0", reload=RELOAD, port=48008)
