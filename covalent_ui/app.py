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
import os
import sys
from datetime import datetime
from distutils.log import debug
from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from pathlib import Path

import networkx as nx
import simplejson
import tailer
from flask import Flask, jsonify, make_response, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files.config import get_config, set_config
from covalent._shared_files.util_classes import Status
from covalent_dispatcher._db.dispatchdb import DispatchDB, encode_result
from covalent_dispatcher._service.app import bp

WEBHOOK_PATH = "/api/webhook"
WEBAPP_PATH = "webapp/build"

app = Flask(__name__, static_folder=WEBAPP_PATH)
app.register_blueprint(bp)
# allow cross-origin requests when API and static files are served separately
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route(WEBHOOK_PATH, methods=["POST"])
def handle_result_update():
    result_update = request.get_json(force=True)
    socketio.emit("result-update", result_update)
    return jsonify({"ok": True})


@app.route("/api/draw", methods=["POST"])
def handle_draw_request():
    draw_request = request.get_json(force=True)

    socketio.emit("draw-request", draw_request)
    return jsonify({"ok": True})


@app.route("/api/results")
def list_results():
    with DispatchDB() as db:
        res = db.get()
    if not res:
        return jsonify([])
    else:
        return jsonify([simplejson.loads(r[1]) for r in res])


@app.route("/api/dev/results/<dispatch_id>")
def fetch_result_dev(dispatch_id):
    results_dir = request.args["resultsDir"]
    result = rm.get_result(dispatch_id, results_dir=results_dir)

    jsonified_result = encode_result(result)

    return app.response_class(jsonified_result, status=200, mimetype="application/json")


@app.route("/api/results/<dispatch_id>")
def fetch_result(dispatch_id):
    with DispatchDB() as db:
        res = db.get([dispatch_id])
    if len(res) > 0:
        response = res[0][1]
        status = 200
    else:
        response = ""
        status = 400

    return app.response_class(response, status=status, mimetype="application/json")


@app.route("/api/results", methods=["DELETE"])
def delete_results():
    dispatch_ids = request.json.get("dispatchIds", [])
    with DispatchDB() as db:
        db.delete(dispatch_ids)
    return jsonify({"ok": True})


@app.route("/api/logoutput/<dispatch_id>")
def fetch_file(dispatch_id):
    path = request.args.get("path")
    n = int(request.args.get("n", 10))

    if not Path(path).expanduser().is_absolute():
        path = os.path.join(get_config("dispatcher.results_dir"), dispatch_id, path)

    try:
        lines = tailer.tail(open(path), n)
    except Exception as ex:
        return make_response(jsonify({"message": str(ex)}), 404)

    return jsonify({"lines": lines})


# catch-all: serve web app static files
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        # static file
        return send_from_directory(app.static_folder, path)
    else:
        # handle all other routes inside web app
        return send_from_directory(app.static_folder, "index.html")


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

    args, unknown = ap.parse_known_args()

    # port to be specified by cli
    if args.port:
        port = int(args.port)
    else:
        port = int(get_config("dispatcher.port"))

    debug = True if args.develop is True else False
    # reload = True if args.develop is True else False
    reload = False

    socketio.run(app, debug=debug, host="0.0.0.0", port=port, use_reloader=reload)
