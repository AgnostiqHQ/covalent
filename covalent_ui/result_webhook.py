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

import json

import requests

import covalent_ui.app as ui_server
from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._shared_files.utils import get_named_params
from covalent_dispatcher._db.dispatchdb import encode_dict, extract_graph, extract_metadata

DEFAULT_PORT = get_config("user_interface.port")

app_log = logger.app_log

# UI server webhook for result updates


def get_ui_url(path):
    baseUrl = f"http://localhost:{DEFAULT_PORT}"
    return f"{baseUrl}{path}"


def send_update(result: Result) -> None:
    """
    Signal UI server about a result update. Note that the server will expect the
    updated result to have been saved to the results directory prior to the
    update.

    Args: result: The updated result object.

    Returns: None
    """

    result_update = json.dumps(
        {
            "event": "result-update",
            "result": {
                "dispatch_id": result.dispatch_id,
                "results_dir": result.results_dir,
                "status": result.status.STATUS,
            },
        },
    )

    try:
        # ignore response
        requests.post(get_ui_url(ui_server.WEBHOOK_PATH), data=result_update)
    except requests.exceptions.RequestException:
        # catch all requests-related exceptions
        app_log.warning("Unable to send result update to UI server.")


def send_draw_request(lattice) -> None:
    """
    Sends a lattice draw request to UI server along with all necessary lattice
    graph data.

    Args: lattice: The lattice to draw with a pre-built graph.

    Returns: None
    """

    graph = lattice.transport_graph.get_internal_graph_copy()

    named_args = {k: v.object_string for k, v in lattice.named_args.items()}
    named_kwargs = {k: v.object_string for k, v in lattice.named_kwargs.items()}

    draw_request = json.dumps(
        {
            "event": "draw-request",
            "payload": {
                "lattice": {
                    "function_string": lattice.workflow_function_string,
                    "doc": lattice.__doc__,
                    "name": lattice.__name__,
                    "inputs": encode_dict({**named_args, **named_kwargs}),
                    "metadata": extract_metadata(lattice.metadata),
                },
                "graph": extract_graph(graph),
            },
        }
    )

    try:
        response = requests.post(get_ui_url("/api/draw"), data=draw_request)
        response.raise_for_status()
    except requests.exceptions.HTTPError as ex:
        app_log.error(ex)
    except requests.exceptions.RequestException:
        app_log.error("Connection failure. Please check Covalent server is running.")
