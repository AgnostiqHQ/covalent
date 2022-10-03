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

import socketio
import uvicorn
from fastapi import Request
from fastapi.templating import Jinja2Templates

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent_dispatcher._db.datastore import DataStore
from covalent_dispatcher._service.app_dask import DaskCluster
from covalent_ui.api.main import app as fastapi_app
from covalent_ui.api.main import sio
from covalent_ui.api.v1.utils.log_handler import log_config

# read env vars configuring server
COVALENT_SERVER_IFACE_ANY = os.getenv("COVALENT_SERVER_IFACE_ANY", "False").lower() in (
    "true",
    "1",
    "t",
)

WEBHOOK_PATH = "/api/webhook"
WEBAPP_PATH = "webapp/build"
STATIC_FILES = {"": WEBAPP_PATH, "/": f"{WEBAPP_PATH}/index.html"}

# Log configuration
app_log = logger.app_log
log_stack_info = logger.log_stack_info
templates = Jinja2Templates(directory=WEBAPP_PATH)


@fastapi_app.get("/{rest_of_path}")
def get_home(request: Request, rest_of_path: str):
    return templates.TemplateResponse("index.html", {"request": request})


socketio_app = socketio.ASGIApp(sio, static_files=STATIC_FILES)
fastapi_app.mount("/", socketio_app)


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
    ap.add_argument(
        "--no-cluster",
        dest="cluster",
        action="store_false",
        required=False,
        help="Start Covalent server without Dask",
    )
    ap.set_defaults(cluster=True)

    args, unknown = ap.parse_known_args()

    # port to be specified by cli
    if args.port:
        port = int(args.port)
    else:
        port = int(get_config("dispatcher.port"))

    host = get_config("dispatcher.address") if not COVALENT_SERVER_IFACE_ANY else "0.0.0.0"

    DEBUG = True if args.develop is True else False
    # reload = True if args.develop is True else False
    RELOAD = False

    # Start dask if no-cluster flag is not specified (covalent stop auto terminates all child processes of this)
    if args.cluster:
        dask_cluster = DaskCluster(name="LocalDaskCluster", logger=app_log)
        dask_cluster.start()

    # Initialize the database
    DataStore(initialize_db=True)

    # Start covalent main app
    uvicorn.run(
        "app:fastapi_app",
        host=host,
        port=port,
        debug=DEBUG,
        reload=RELOAD,
        log_config=log_config(),
    )
