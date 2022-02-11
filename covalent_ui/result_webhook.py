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

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config

from .app import WEBHOOK_PATH

DEFAULT_PORT = get_config("user_interface.port")

app_log = logger.app_log

# UI server webhook for result updates
WEBHOOK_BASE_URL = f"http://localhost:{DEFAULT_PORT}"
WEBHOOK_URL = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"


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
            "event": "change",
            "result": {
                "dispatch_id": result.dispatch_id,
                "results_dir": result.results_dir,
                "status": result.status.STATUS,
            },
        },
    )

    try:
        # ignore response
        requests.post(WEBHOOK_URL, data=result_update)
    except requests.exceptions.RequestException:
        # catch all requests-related exceptions
        app_log.warning("Unable to send result update to UI server.")
