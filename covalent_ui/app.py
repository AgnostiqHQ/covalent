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

import argparse
import os
from multiprocessing import Pipe

import socketio
import uvicorn
from fastapi import Request
from fastapi.templating import Jinja2Templates

from covalent._shared_files import logger
from covalent._shared_files.config import get_config, update_config
from covalent_dispatcher._service.app_dask import DaskCluster
from covalent_dispatcher._triggers_app import triggers_only_app  # nopycln: import
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


socketio_app = socketio.ASGIApp(
    sio,
    static_files=STATIC_FILES,
)
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

    ap.add_argument(
        "--no-triggers",
        dest="no_triggers",
        action="store_true",  # this means default is False
        required=False,
        help="Start Covalent server without the Triggers server",
    )

    ap.add_argument(
        "--triggers-only",
        dest="triggers_only",
        action="store_true",  # this means default is False
        required=False,
        help="Start only the Triggers server",
    )

    ap.set_defaults(cluster=True)

    args, unknown = ap.parse_known_args()

    # port to be specified by cli
    port = int(args.port) if args.port else int(get_config("dispatcher.port"))
    host = "0.0.0.0" if COVALENT_SERVER_IFACE_ANY else get_config("dispatcher.address")

    DEBUG = args.develop is True

    # reload = True if args.develop is True else False
    RELOAD = False

    # Start dask if no-cluster flag is not specified (covalent stop auto terminates all child processes of this)
    if args.cluster:
        parent_conn, child_conn = Pipe()
        dask_cluster = DaskCluster(name="LocalDaskCluster", logger=app_log, conn=child_conn)
        dask_cluster.start()
        dask_config = parent_conn.recv()
        update_config(dask_config)

    app_name = "app:fastapi_app"
    if args.triggers_only:
        from covalent_dispatcher._triggers_app import trigger_only_router  # nopycln: import

        app_name = "app:triggers_only_app"
        fastapi_app.include_router(trigger_only_router, prefix="/api", tags=["Triggers"])
    elif args.no_triggers:
        import covalent_dispatcher._triggers_app.app as tr_app

        tr_app.disable_triggers = True

    # Start covalent main app
    uvicorn.run(
        app_name,
        host=host,
        port=port,
        debug=DEBUG,
        reload=RELOAD,
        log_config=log_config(),
    )
