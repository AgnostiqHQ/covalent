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

import cloudpickle as pickle
# from flask import Blueprint, Flask, Response, jsonify, request
from fastapi import APIRouter, Request, File

import covalent_dispatcher as dispatcher

api_router = APIRouter()


# @bp.route("/submit", methods=["POST"])
@api_router.post("/submit")
async def submit(pickled_res: bytes = File(...)):
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

    result_object = pickle.loads(pickled_res)
    dispatch_id = dispatcher.run_dispatcher(result_object)

    return {"dispatch_id": dispatch_id}


# @bp.route("/cancel", methods=["POST"])
@api_router.delete("/cancel/{dispatch_id}")
async def cancel(dispatch_id: str):
    """
    Function to accept the cancel request of
    a dispatch.

    Args:
        None

    Returns:
        Flask Response object confirming that the dispatch
        has been cancelled.
    """

    dispatcher.cancel_running_dispatch(dispatch_id)

    return {"response": f"Dispatch {dispatch_id} cancelled."}
