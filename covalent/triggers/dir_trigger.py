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
                     Possible options can be a subset of: `["created", "deleted", "modified", "moved", "closed"]`.
        batch_size: The number of changes to wait for before performing the trigger action, default is 1.
        recursive: Whether to recursively watch the directory, default is False.

    Attributes:
        self.dir_path: Path to the file/dir which is to be observed for events
        self.event_names: List of event names on which to perform the trigger action.
                          Possible options can be a subset of: `["created", "deleted", "modified", "moved", "closed"]`
        self.batch_size: The number of events to wait for before performing the trigger action, default is `1`.
        self.recursive: Whether to recursively watch the directory, default is False.
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
        recursive: bool = False,
    ):
        super().__init__(lattice_dispatch_id, dispatcher_addr, triggers_server_addr)

        self.dir_path = dir_path

        if isinstance(event_names, str):
            event_names = [event_names]
        self.event_names = event_names

        self.batch_size = batch_size
        self.recursive = recursive

        self.observe_blocks = False
        self.event_handler = None

    def attach_methods_to_handler(self) -> None:
        """
        Dynamically attaches and overrides the "on_*" methods to the handler
        depending on which ones are requested by the user.

        Args:
            event_names: List of event names upon which to perform a trigger action
        """

        app_log.warning("Attaching methods to dir handler")

        self.n_changes = 0

        def proxy_trigger(_, event_object):
            self.n_changes += 1
            if self.n_changes == self.batch_size:
                self.trigger()
                self.n_changes = 0

        for en in self.event_names:
            func_name = self.event_handler.supported_event_to_func_names[en]
            proxy_trigger.__name__ = func_name
            setattr(self.event_handler, func_name, MethodType(proxy_trigger, self.event_handler))

    def observe(self) -> None:
        """
        Start observing the file/dir for any possible events among the ones
        mentioned in `self.event_names`.
        Currently only supports running within the Covalent/Triggers server.
        """

        app_log.warning(f"In DirTrigger's observe, dir path is: {self.dir_path}")

        # Resolving the path at the place where observation will happen
        self.dir_path = str(Path(self.dir_path).expanduser().resolve())

        self.event_loop = asyncio.get_running_loop()

        self.event_handler = DirEventHandler()

        # Attach methods before scheduling the observer
        self.attach_methods_to_handler()

        self.observer = Observer()
        print("Schedule is: ", type(self.observer.schedule))
        self.observer.schedule(self.event_handler, self.dir_path, recursive=self.recursive)
        self.observer.start()

    def stop(self) -> None:
        """
        Stop observing the file or directory for changes.
        """
        self.observer.stop()
        self.observer.join()
