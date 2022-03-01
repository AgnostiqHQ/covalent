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

import covalent.executor as covalent_executor
from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import Status
from covalent._shared_files.utils import get_named_params
from covalent_dispatcher._service.app import bp

WEBHOOK_PATH = "/api/webhook"
WEBAPP_PATH = "webapp/build"
DEFAULT_PORT = 5000

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
    path = request.args["resultsDir"]
    dispatch_ids = [dir for dir in os.listdir(path) if os.path.isdir(os.path.join(path, dir))]
    return jsonify(dispatch_ids)


def encode_result(obj):
    if isinstance(obj, Status):
        return obj.STATUS
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def extract_graph_node(node):
    # doc string
    f = node.get("function")
    if f is not None:
        node["doc"] = node["function"].get_deserialized().__doc__

    # metadata
    extract_executor_info(node.get("metadata"))

    # prevent JSON encoding
    node["kwargs"] = encode_dict(node.get("kwargs"))

    # remove unused fields
    node.pop("function", None)
    node.pop("node_name", None)

    return node


def encode_dict(d):
    """Avoid JSON encoding when python str() suffices"""
    if not isinstance(d, dict):
        return d
    return {k: str(v) for (k, v) in d.items()}


def extract_executor_info(metadata):
    # executor details
    try:
        name = metadata["executor"]
        executor = covalent_executor._executor_manager.get_executor(name=name)

        if executor is not None:
            # extract attributes
            metadata["executor"] = encode_dict(executor.__dict__)
            if isinstance(name, str):
                metadata["executor_name"] = name
            else:
                metadata["executor_name"] = f"<{executor.__class__.__name__}>"
    except (KeyError, AttributeError):
        pass


def extract_graph(graph):
    graph = nx.json_graph.node_link_data(graph)
    nodes = list(map(extract_graph_node, graph["nodes"]))
    return {
        "nodes": nodes,
        "links": graph["links"],
    }


@app.route("/api/results/<dispatch_id>")
def fetch_result(dispatch_id):
    results_dir = request.args["resultsDir"]

    result = rm.get_result(dispatch_id, results_dir=results_dir)
    extract_executor_info(result.lattice.metadata)

    lattice = result.lattice
    ((named_args, named_kwargs),) = (
        get_named_params(lattice.workflow_function, lattice.args, lattice.kwargs),
    )

    response = {
        "dispatch_id": result.dispatch_id,
        "status": result.status,
        "result": result.result,
        "start_time": result.start_time,
        "end_time": result.end_time,
        "results_dir": result.results_dir,
        "error": result.error,
        "lattice": {
            "function_string": lattice.workflow_function_string,
            "doc": lattice.__doc__,
            "name": lattice.__name__,
            "inputs": encode_dict({**named_args, **named_kwargs}),
            "metadata": lattice.metadata,
        },
        "graph": extract_graph(result.lattice.transport_graph._graph),
    }

    # Use simplejson/ignore_nan=True to handle NaN/Infinity constants
    response = simplejson.dumps(response, default=encode_result, ignore_nan=True)

    return app.response_class(response, status=200, mimetype="application/json")


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
    ap.add_argument(
        "-l",
        "--log-file",
        required=False,
        help="Path to log file that will be written to by server.",
    )
    ap.add_argument("-p", "--port", required=False, help="Server port number.")
    ap.add_argument(
        "-d",
        "--develop",
        required=False,
        action="store_true",
        help="Start the server in developer mode.",
    )
    args, unknown = ap.parse_known_args()
    # log file to be specified by cli
    if args.log_file:
        import logging

        log_file = args.log_file
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
        )
    # port to be specified by cli
    if args.port:
        port = int(args.port)
    else:
        port = DEFAULT_PORT
    debug = True if args.develop is True else False
    socketio.run(app, debug=debug, host="0.0.0.0", port=port)
