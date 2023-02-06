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
from pathlib import Path
from types import MethodType

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from covalent._shared_files import logger

from .base import BaseTrigger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class DirEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        self.supported_event_to_func_names = {
            "created": "on_created",
            "deleted": "on_deleted",
            "modified": "on_modified",
            "moved": "on_moved",
            "closed": "on_closed",
        }


class DirTrigger(BaseTrigger):
    """
    Directory or File based trigger which watches for events in said file/dir
    and performs a trigger action whenever they happen.

    Args:
        dir_path: Path to the file/dir which is to be observed for events
        event_names: List of event names on which to perform the trigger action.
                     Possible options can be a subset of: `["created", "deleted", "modified", "moved", "closed"]`
        batch_size: The number of changes to wait for before performing the trigger action, default is 1.

    Attributes:
        self.dir_path: Path to the file/dir which is to be observed for events
        self.event_names: List of event names on which to perform the trigger action.
                          Possible options can be a subset of: `["created", "deleted", "modified", "moved", "closed"]`
        self.batch_size: The number of events to wait for before performing the trigger action, default is `1`.
        self.n_changes: Number of events since last trigger action. Whenever `self.n_changes == self.batch_size` a trigger action happens.
    """

    def __init__(
        self,
        dir_path,
        event_names,
        batch_size: int = 1,
        lattice_dispatch_id: str = None,
        dispatcher_addr: str = None,
        triggers_server_addr: str = None,
    ):
        super().__init__(lattice_dispatch_id, dispatcher_addr, triggers_server_addr)

        self.dir_path = str(Path(dir_path).expanduser().resolve())
        self.batch_size = batch_size

        if isinstance(event_names, str):
            event_names = [event_names]
        self.event_names = event_names

        self.observe_blocks = False

    def attach_methods_to_handler(self, event_names: list) -> None:
        """
        Dynamically attaches and overrides the "on_*" methods to the handler
        depending on which ones are requested by the user.

        Args:
            event_names: List of event names upon which to perform a trigger action
        """

        self.n_changes = 0

        def proxy_trigger(*args, **kwargs):
            self.n_changes += 1
            if self.n_changes == self.batch_size:
                self.trigger()
                self.n_changes = 0

        for en in event_names:
            func_name = self.event_handler.supported_event_to_func_names[en]
            proxy_trigger.__name__ = func_name
            setattr(self.event_handler, func_name, MethodType(proxy_trigger, self.event_handler))

    def observe(self) -> None:
        """
        Start observing the file/dir for any possible events among the ones
        mentioned in `self.event_names`.

        Currently only supports running within the Covalent/Triggers server.
        """
        self.event_loop = asyncio.get_running_loop()

        self.event_handler = DirEventHandler()

        # Attach methods before scheduling the observer
        self.attach_methods_to_handler(self.event_names)

        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.dir_path)
        self.observer.start()

    def stop(self) -> None:
        """
        Stop observing the file or directory for changes.
        """
        self.observer.stop()
        self.observer.join()
