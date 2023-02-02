# Copyright 2023 Agnostiq Inc.
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

import asyncio

from fastapi import APIRouter, FastAPI, Request

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent.triggers import available_triggers
from covalent_dispatcher._service.app import get_result
from covalent_dispatcher.entry_point import run_dispatcher, run_redispatch

app_log = logger.app_log
log_stack_info = logger.log_stack_info


router = APIRouter()
triggers_only_app = FastAPI()

active_triggers = {}


@router.post("/triggers/start")
async def start(request: Request):
    trigger_data = await request.json()
    lattice_dispatch_id, name, dir_path, event_names = (
        trigger_data["lattice_dispatch_id"],
        trigger_data["name"],
        trigger_data["dir_path"],
        trigger_data["event_names"],
    )
    trigger = available_triggers[name](dir_path, event_names)

    trigger.start(lattice_dispatch_id, triggered_dispatch)

    active_triggers[lattice_dispatch_id] = trigger

    app_log.warning(f"Started trigger with id: {lattice_dispatch_id}")


@router.post("/triggers/stop")
async def stop(request: Request):
    dispatch_ids = await request.json()

    triggers = [(d_id, active_triggers[d_id]) for d_id in dispatch_ids]

    for d_id, trigger in triggers:
        trigger.stop()
        app_log.warning(f"Stopped trigger with lattice dispatch id: {d_id}")


triggers_only_app.include_router(router, prefix="/api", tags=["Triggers"])


def triggered_dispatch(self, event):

    status = asyncio.run_coroutine_threadsafe(
        get_result(self.lattice_dispatch_id, status_only=True), self.covalent_event_loop
    ).result()["status"]

    if status == str(Result.NEW_OBJ):
        # To continue pending dispatch
        future = asyncio.run_coroutine_threadsafe(
            run_dispatcher(None, pending_dispatch_id=self.lattice_dispatch_id),
            self.covalent_event_loop,
        )
        same_dispatch_id = future.result()
        app_log.warning(f"Initiating run for same dispatch_id: {same_dispatch_id}")
    else:
        # To run new redispatch
        future = asyncio.run_coroutine_threadsafe(
            run_redispatch(self.lattice_dispatch_id, None, None, False),
            self.covalent_event_loop,
        )
        new_dispatch_id = future.result()
        app_log.warning(f"Redispatching, new dispatch_id: {new_dispatch_id}")

    app_log.warning(f"File path that triggered this event: {event.src_path}")
