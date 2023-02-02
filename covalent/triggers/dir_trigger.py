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
from types import MethodType

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from covalent._shared_files import logger

from .base import BaseTrigger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


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


# To dynamically attach and override "on_*" methods to the handler
# depending on which ones are requested by the user
def attach_methods_to_handler(
    event_handler: DirEventHandler, event_names: list, triggered_dispatch
):

    for en in event_names:
        func_name = event_handler.supported_event_to_func_names[en]
        triggered_dispatch.__name__ = func_name
        setattr(event_handler, func_name, MethodType(triggered_dispatch, event_handler))

    return event_handler


class DirTrigger(BaseTrigger):
    def __init__(self, dir_path, event_names) -> None:
        self.dir_path = dir_path

        if isinstance(event_names, str):
            event_names = [event_names]

        self.event_names = event_names

    def start(self, lattice_dispatch_id, triggered_dispatch):

        covalent_event_loop = asyncio.get_running_loop()

        event_handler = DirEventHandler(lattice_dispatch_id, covalent_event_loop)
        event_handler = attach_methods_to_handler(
            event_handler, self.event_names, triggered_dispatch
        )

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
