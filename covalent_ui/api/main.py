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

"""Fastapi init"""

import fcntl
import logging
import os
import pty
import select
import struct
import subprocess
import termios

import socketio
from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent_ui.api.v1.routes import routes

file_descriptor = None
child_process_id = None

# Config
WEBHOOK_PATH = "/api/webhook"
address = get_config("user_interface.address")
port = str(get_config("user_interface.dev_port"))
socket_port = str(get_config("user_interface.port"))
origins = [f"http://{address}:{port}"]
socket_origins = [f"http://{address}:{port}", f"http://{address}:{socket_port}"]

app_log = logger.app_log

app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi")


@sio.on("message")
async def chat_message(sid, data):
    await sio.emit("draw-request", "hi ")


app.include_router(routes.routes)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def set_winsize(fd, row, col, xpix=0, ypix=0):
    logging.debug("setting window size with termios")
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


async def read_and_forward_pty_output():
    max_read_bytes = 1024 * 10
    while True:
        await sio.sleep(0.01)
        if file_descriptor:
            timeout_sec = 0
            (data_ready, _, _) = select.select([file_descriptor], [], [], timeout_sec)
            if data_ready:
                output = os.read(file_descriptor, max_read_bytes).decode()
                await sio.emit("pty-output", {"output": output})


@sio.on("pty-input")
def pty_input(sid, data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if file_descriptor:
        os.write(file_descriptor, data["input"].encode())


@sio.on("resize")
def resize(sid, data):
    if file_descriptor:
        logging.debug(f"Resizing window to {data['rows']}x{data['cols']}")
        set_winsize(file_descriptor, data["rows"], data["cols"])


@sio.on("start_terminal")
async def chat_message(*args):
    logging.info("new client connected")
    global child_process_id
    if child_process_id:
        return
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        subprocess.run(["bash"])
    else:
        child_process_id = child_pid
        global file_descriptor
        file_descriptor = fd
        set_winsize(file_descriptor, 50, 50)
        sio.start_background_task(read_and_forward_pty_output)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=400,
        content=jsonable_encoder({"detail": exc.detail}),
    )


@app.post(WEBHOOK_PATH)
async def handle_result_update(result_update: dict):
    await sio.emit("result-update", result_update)
    return {"ok": True}


@app.post("/api/draw")
async def handle_draw_request(draw_request: dict):
    await sio.emit("draw_request", draw_request)
    return {"ok": True}
