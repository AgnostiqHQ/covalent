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

import argparse

# from covalent_dispatcher._service.app import bp
import asyncio
import os
import sys
from datetime import datetime
from distutils.log import debug
from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from pathlib import Path

import networkx as nx
import simplejson
import tailer
from dask.distributed import Client, LocalCluster
from fastapi import APIRouter, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi_socketio import SocketManager
from starlette.exceptions import HTTPException

from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files.config import get_config, set_config
from covalent._shared_files.util_classes import Status
from covalent_dispatcher._db.dispatchdb import DispatchDB, encode_result
from covalent_dispatcher._service.app import api_router

# from flask import Flask, jsonify, make_response, request, send_from_directory
# from flask_cors import CORS
# from flask_socketio import SocketIO





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
            # if e.status_code == 404:
            #     # return /index.html
            #     response = await super().get_response(".", scope)
            response = await super().get_response(".", scope)
        return response


WEBHOOK_PATH = "/api/webhook"


app = FastAPI(title="Covalent UI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


sio = SocketManager(app=app)

app.include_router(api_router, prefix="/api")

@app.post(WEBHOOK_PATH)
def handle_result_update(request: Request):
    result_update = request.get_json(force=True)
    sio.emit("result-update", result_update)
    return {"ok": True}



@app.post("/api/draw")
def handle_draw_request(request: Request):
    draw_request = request.get_json(force=True)

    sio.emit("draw-request", draw_request)
    return {"ok": True}



@app.get("/api/results")
def list_results():
    with DispatchDB() as db:
        res = db.get()
    return jsonable_encoder([simplejson.loads(r[1]) for r in res]) if res else jsonable_encoder([])


# @app.route("/api/dev/results/<dispatch_id>")
@app.get("/api/dev/results/{dispatch_id}")
def fetch_result_dev(dispatch_id: str, request: Request):
    results_dir = request.args["resultsDir"]
    result = rm.get_result(dispatch_id, results_dir=results_dir)

    jsonified_result = encode_result(result)

    return app.response_class(jsonified_result, status=200, mimetype="application/json")


# @app.route("/api/results/<dispatch_id>")
@app.get("/api/results/{dispatch_id}")
def fetch_result(dispatch_id: str):
    with DispatchDB() as db:
        res = db.get([dispatch_id])
    if len(res) > 0:
        response = res[0][1]
        status = 200
    else:
        response = ""
        status = 400

    return JSONResponse(content=jsonable_encoder(response), status_code=status)



@app.delete("/api/results")
def delete_results(request: Request):
    dispatch_ids = request.json.get("dispatchIds", [])
    with DispatchDB() as db:
        db.delete(dispatch_ids)
    return {"ok": True}



@app.get("/api/logoutput/{dispatch_id}")
def fetch_file(dispatch_id: str, request: Request):
    path = request.query_params["path"]
    n = int(request.query_params("n") or 10)

    if not Path(path).expanduser().is_absolute():
        path = os.path.join(get_config("dispatcher.results_dir"), dispatch_id, path)

    try:
        lines = tailer.tail(open(path), n)
    except Exception as ex:
        return JSONResponse(content=jsonable_encoder({"message": str(ex)}), status_code=404)

    return {"lines": lines}


app.mount("/", SinglePageApp(directory=f"{BASE_PATH}{FRONTEND_PATH}", html=True), name="static")


# # catch-all: serve web app static files
# @app.route("/", defaults={"path": ""})
# @app.route("/<path:path>")
# def serve(path):
#     if path != "" and os.path.exists(f"{app.static_folder}/{path}"):
#         # static file
#         return send_from_directory(app.static_folder, path)
#     else:
#         # handle all other routes inside web app
#         return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":

    # Creating process based cluster and limiting each worker's memory to 1 GiB
    cluster = LocalCluster(memory_limit="1GiB")
    set_config("dask_scheduler_address", cluster.scheduler_address)
    dask_client = Client(cluster)


    ap = argparse.ArgumentParser()

    ap.add_argument("-p", "--port", required=False, help="Server port number.")
    ap.add_argument(
        "-d",
        "--develop",
        required=False,
        action="store_true",
        help="Start the server in developer mode.",
    )

    args, unknown = ap.parse_known_args()

    # port to be specified by cli
    port = int(args.port) if args.port else int(get_config("dispatcher.port"))

    debug = args.develop is True

    # reload = True if args.develop is True else False
    reload = False

    # socketio.run(app, debug=debug, host="0.0.0.0", port=port, use_reloader=reload)

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        log_level="debug",
        reload=reload,
        debug=debug,
    )
