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


import asyncio
from types import MethodType

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from covalent._results_manager import Result
from covalent._shared_files import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


SLEEP = 10

all_triggers = {}


def triggered_dispatch(self, event):
    from .._service.app import get_result
    from ..entry_point import run_dispatcher, run_redispatch

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


class DirEventHandler(FileSystemEventHandler):
    def __init__(self, lattice_dispatch_id, covalent_event_loop) -> None:
        self.lattice_dispatch_id = lattice_dispatch_id
        self.covalent_event_loop = covalent_event_loop

        self.supported_event_to_func_names = {
            "created": "on_created",
            "deleted": "on_deleted",
            "modified": "on_modified",
            "moved": "on_moved",
            "closed": "on_closed",
        }


def attach_methods_to_handler(event_handler: DirEventHandler, event_names: list):

    for en in event_names:
        func_name = event_handler.supported_event_to_func_names[en]
        triggered_dispatch.__name__ = func_name
        setattr(event_handler, func_name, MethodType(triggered_dispatch, event_handler))

    return event_handler


class DirTrigger:
    def __init__(self, dir_path, event_names) -> None:
        self.dir_path = dir_path

        if isinstance(event_names, str):
            event_names = [event_names]

        self.event_names = event_names

    def start(self, lattice_dispatch_id):

        covalent_event_loop = asyncio.get_running_loop()

        event_handler = DirEventHandler(lattice_dispatch_id, covalent_event_loop)
        event_handler = attach_methods_to_handler(event_handler, self.event_names)

        self.observer = Observer()
        self.observer.schedule(event_handler, self.dir_path)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def to_dict(self):
        return {
            "name": str(self.__class__.__name__),
            "dir_path": self.dir_path,
            "event_names": self.event_names,
        }


def start_triggers(trigger_dict):  # sourcery skip: use-assigned-variable

    if trigger_dict:

        lattice_dispatch_id, name, dir_path, event_names = (
            trigger_dict["lattice_dispatch_id"],
            trigger_dict["name"],
            trigger_dict["dir_path"],
            trigger_dict["event_names"],
        )
        trigger = globals()[name](dir_path, event_names)

        trigger.start(lattice_dispatch_id)

        all_triggers[lattice_dispatch_id] = trigger

        app_log.warning(f"Started trigger with id: {lattice_dispatch_id}")


def stop_triggers(dispatch_ids):

    triggers = [(d_id, all_triggers[d_id]) for d_id in dispatch_ids]

    for d_id, trigger in triggers:
        trigger.stop()
        app_log.warning(f"Stopped trigger with lattice dispatch id: {d_id}")
