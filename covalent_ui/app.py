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

import os
from datetime import datetime
from logging.handlers import DEFAULT_TCP_LOGGING_PORT
from pathlib import Path

import networkx as nx
import simplejson
import tailer
from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from flask_socketio import SocketIO

from covalent._results_manager import Result
from covalent._results_manager import results_manager as rm
from covalent._shared_files.config import get_config
from covalent._shared_files.util_classes import Status
from covalent.executor import _executor_manager

WEBHOOK_PATH = "/api/webhook"
WEBAPP_PATH = "webapp/build"

app = Flask(__name__, static_folder=WEBAPP_PATH)
# allow cross-origin requests when API and static files are served separately
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route(WEBHOOK_PATH, methods=["POST"])
def handle_result_update():
    result_update = request.get_json(force=True)
    socketio.emit("result-update", result_update)
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
    node.pop("function")
    node.pop("node_name")

    return node


def encode_dict(d):
    """ Avoid JSON encoding when python str() suffices """
    if not isinstance(d, dict):
        return d
    return {k: str(v) for (k, v) in d.items()}


def extract_executor_info(metadata):
    # executor details
    try:
        backend = metadata["backend"]
        executor = _executor_manager.get_executor(name=backend)
        if executor is not None:
            # extract attributes
            metadata["executor"] = encode_dict(executor.__dict__)
            if not isinstance(backend, str):
                # if not named, replace with class name
                metadata["backend"] = f"<{executor.__class__.__name__}>"
    except (KeyError, AttributeError) as e:
        pass


def extract_graph(result):
    graph = nx.json_graph.node_link_data(result.lattice.transport_graph._graph)
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

    response = {
        "dispatch_id": result.dispatch_id,
        "status": result.status,
        "result": result.result,
        "start_time": result.start_time,
        "end_time": result.end_time,
        "results_dir": result.results_dir,
        "lattice": {
            "function_string": result.lattice.workflow_function_string,
            "doc": result.lattice.__doc__,
            "name": result.lattice.__name__,
            "kwargs": encode_dict(result.lattice.kwargs),
            "metadata": result.lattice.metadata,
        },
        "graph": extract_graph(result),
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
    socketio.run(app)
