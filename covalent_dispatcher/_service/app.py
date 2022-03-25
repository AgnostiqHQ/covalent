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

from typing import Union

import cloudpickle as pickle
from flask import Blueprint, Flask, Response, jsonify, request

import covalent_dispatcher as dispatcher
from covalent._shared_files import logger

bp = Blueprint("dispatcher", __name__, url_prefix="/api")
app_log = logger.app_log


def check_empty_post() -> Union[Response, None]:
    """
    Function to check if a request has empty body

    Args:
        None
    Returns:
        Reponse: An Http status code 400 if body of the post request is empty.
        None: Otherwise.
    """
    if request.method == "POST" and not request.content_length:
        return Response(response="Empty request body.", status=400)
    return None


bp.before_app_request(check_empty_post)


@bp.route("/submit", methods=["POST"])
def submit() -> Response:
    """
    Function to accept the submit request of
    new dispatch and return the dispatch id
    back to the client.

    Args:
        None

    Returns:
        The dispatch id in a json format
        returned as a Flask Response object.
    """

    data = request.get_data()
    result_object = pickle.loads(data)
    app_log.debug("submit")
    app_log.debug("results directory is " + result_object._results_dir)
    dispatch_id = dispatcher.run_dispatcher(result_object)

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
