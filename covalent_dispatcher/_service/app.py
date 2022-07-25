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

import codecs
from concurrent.futures import ThreadPoolExecutor

import cloudpickle as pickle
from flask import Blueprint, Response, jsonify, make_response, request
from sqlalchemy.orm import Session

import covalent_dispatcher as dispatcher
from covalent._data_store.models import Lattice
from covalent._results_manager.result import Result
from covalent._results_manager.results_manager import result_from
from covalent._results_manager.write_result_to_db import MissingLatticeRecordError

from .._db.dispatchdb import DispatchDB

bp = Blueprint("dispatcher", __name__, url_prefix="/api")


@bp.before_app_first_request
def start_pools():
    global workflow_pool
    global tasks_pool

    workflow_pool = ThreadPoolExecutor()
    tasks_pool = ThreadPoolExecutor()


@bp.route("/submit", methods=["POST"])
def submit() -> Response:
    """
    Function to accept the submit request of
    new dispatch and return the dispatch id
    back to the client.

    Args:
        None

    Returns:
        dispatch_id: The dispatch id in a json format
                     returned as a Flask Response object.
    """

    json_lattice = request.get_data()

    dispatch_id = dispatcher.run_dispatcher(json_lattice, workflow_pool, tasks_pool)

    return jsonify(dispatch_id)


@bp.route("/cancel", methods=["POST"])
def cancel() -> Response:
    """
    Function to accept the cancel request of
    a dispatch.

    Args:
        None

    Returns:
        Flask Response object confirming that the dispatch
        has been cancelled.
    """
    dispatch_id = request.get_data().decode("utf-8")

    dispatcher.cancel_running_dispatch(dispatch_id)

    return jsonify(f"Dispatch {dispatch_id} cancelled.")


@bp.route("/db-path", methods=["GET"])
def db_path() -> Response:
    db_path = DispatchDB()._dbpath
    return jsonify(db_path)


@bp.route("/result/<dispatch_id>", methods=["GET"])
def get_result(dispatch_id) -> Response:
    args = request.args
    wait = args.get("wait", default=False, type=lambda v: v.lower() == "true")
    status_only = args.get("status_only", default=False, type=lambda v: v.lower() == "true")
    while True:
        with Session(DispatchDB()._get_data_store().engine) as session:
            lattice_record = (
                session.query(Lattice).where(Lattice.dispatch_id == dispatch_id).first()
            )
        try:
            if not lattice_record:
                return (
                    jsonify(
                        {"message": f"The requested dispatch ID {dispatch_id} was not found."}
                    ),
                    404,
                )
            elif not wait or lattice_record.status in [
                str(Result.COMPLETED),
                str(Result.FAILED),
                str(Result.CANCELLED),
                str(Result.POSTPROCESSING_FAILED),
                str(Result.PENDING_POSTPROCESSING),
            ]:
                output = {
                    "id": dispatch_id,
                    "status": lattice_record.status,
                }
                if not status_only:
                    output["result"] = codecs.encode(
                        pickle.dumps(result_from(lattice_record)), "base64"
                    ).decode()
                return jsonify(output)

        except (FileNotFoundError, EOFError):
            if wait:
                continue
            response = make_response(
                jsonify(
                    {
                        "message": "Result not ready to read yet. Please wait for a couple of seconds."
                    }
                ),
                503,
            )
            response.retry_after = 2
            return response
