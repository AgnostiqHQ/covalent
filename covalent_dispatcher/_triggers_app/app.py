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
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from inspect import signature

from fastapi import APIRouter, FastAPI, HTTPException, Request

from covalent._shared_files import logger
from covalent.triggers import BaseTrigger, available_triggers

disable_triggers = False

app_log = logger.app_log
log_stack_info = logger.log_stack_info

router = APIRouter()
triggers_only_app = FastAPI()

active_triggers = {}


def init_trigger(tr_dict: dict) -> BaseTrigger:
    tr_name = tr_dict.pop("name")

    # Loading trigger's class
    tr_class = available_triggers[tr_name]

    # Handling required constructor params
    sig = signature(tr_class.__init__)
    init_params = {}
    for k, v in tr_dict.copy().items():
        if sig.parameters.get(k):
            init_params[k] = v
            tr_dict.pop(k)

    trigger = tr_class(**init_params)

    # Setting all other values
    for k, v in tr_dict.items():
        setattr(trigger, k, v)

    return trigger


@lru_cache
def get_threadpool():
    return ThreadPoolExecutor()


@router.post("/triggers/register")
async def register_and_observe(request: Request):
    if disable_triggers:
        raise HTTPException(status_code=412, detail="Trigger endpoints are disabled as requested")

    thread_pool = get_threadpool()

    trigger_dict = await request.json()

    trigger = init_trigger(trigger_dict)

    if trigger.use_internal_funcs:
        trigger.event_loop = asyncio.get_running_loop()

    if trigger.observe_blocks:
        thread_pool.submit(trigger.observe)
    else:
        trigger.observe()

    lattice_did = trigger.lattice_dispatch_id

    if active_triggers.get(lattice_did):
        active_triggers[lattice_did].append(trigger)
    else:
        active_triggers[lattice_did] = [trigger]

    app_log.debug(f"Started trigger with id: {lattice_did}")


@router.post("/triggers/stop_observe")
async def stop_observe(request: Request):
    if disable_triggers:
        raise HTTPException(status_code=412, detail="Trigger endpoints are disabled as requested")

    dispatch_ids = await request.json()

    for d_id in dispatch_ids:
        for trigger in active_triggers[d_id]:
            trigger.stop()
            app_log.debug(f"Stopped observing on trigger(s) with lattice dispatch id: {d_id}")


triggers_only_app.include_router(router, prefix="/api", tags=["Triggers"])
