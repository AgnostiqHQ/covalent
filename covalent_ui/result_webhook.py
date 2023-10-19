# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import aiohttp
import requests

import covalent_ui.app as ui_server
from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.utils import get_ui_url
from covalent_dispatcher._db.dispatchdb import encode_dict, extract_graph, extract_metadata

app_log = logger.app_log

# UI server webhook for result updates


async def send_update(result: Result) -> None:
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
        timeout = aiohttp.ClientTimeout(total=1)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                get_ui_url(ui_server.WEBHOOK_PATH), json=json.loads(result_update)
            ) as resp:
                status = resp.status
                text = await resp.text()
                app_log.debug(f"send_update received response {status}, {text}")
    except Exception as ex:
        # catch all requests-related exceptions
        app_log.debug(f"Unable to send result update to UI server: {ex}")


def send_draw_request(lattice) -> None:
    """
    Sends a lattice draw request to UI server along with all necessary lattice
    graph data.

    Args: lattice: The lattice to draw with a pre-built graph.

    Returns: None
    """

    graph = lattice.transport_graph.get_internal_graph_copy()

    named_args = lattice.named_args.get_deserialized()
    named_kwargs = lattice.named_kwargs.get_deserialized()

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
