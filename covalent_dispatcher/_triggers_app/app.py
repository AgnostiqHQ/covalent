# Copyright 2023 Agnostiq Inc.
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

"""Triggers server API routes and standalone app definition"""


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
trigger_only_router = APIRouter()
triggers_only_app = FastAPI()

active_triggers = {}


def init_trigger(tr_dict: dict) -> BaseTrigger:
    """
    Recreate the trigger from its dictionary representation

    Args:
        tr_dict: Dictionary containing a representation of a Trigger

    Returns:
        Trigger object, descendant of "BaseTrigger" class
    """

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


@trigger_only_router.get("/triggers/healthcheck")
async def healthcheck(request: Request):
    return {"status": "ok"}


@router.get("/triggers/status")
def trigger_server_status(request: Request):
    if disable_triggers:
        return {"status": "disabled"}
    else:
        return {"status": "running"}


@router.post("/triggers/register")
async def register_and_observe(request: Request):
    """
    Register and start the trigger's observe method
    """

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
    """
    Stop the triggers in a set of given dispatch ids
    """

    if disable_triggers:
        raise HTTPException(status_code=412, detail="Trigger endpoints are disabled as requested")

    dispatch_ids = await request.json()

    for d_id in dispatch_ids:
        for trigger in active_triggers[d_id]:
            trigger.stop()
            app_log.debug(f"Stopped observing on trigger(s) with lattice dispatch id: {d_id}")


triggers_only_app.include_router(router, prefix="/api", tags=["Triggers"])
triggers_only_app.include_router(trigger_only_router, prefix="/api", tags=["Triggers"])
