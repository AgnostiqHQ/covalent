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


import uuid

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from covalent._shared_files import logger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


SLEEP = 10

all_triggers = {}


class DirEventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()
        self.n_times = 0

    def on_modified(self, event):
        super().on_modified(event)
        self.n_times += 1

        app_log.warning(f"File modified {self.n_times}")


class DirTrigger:
    def __init__(self, dir_path, event_name=None) -> None:
        self.dir_path = dir_path
        self.event_name = event_name or "modified"

    def start(self):
        event_handler = DirEventHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, self.dir_path)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


def start_triggers():
    # do create_task for all the triggers here
    trigger = DirTrigger(dir_path="/home/neptune/dev/covalent/covalent_dispatcher/_core/")
    trigger.start()

    t_id = str(uuid.uuid4())[-4:]
    all_triggers[t_id] = trigger

    app_log.warning(f"Started trigger with id: {t_id}")

    return t_id


def stop_triggers(t_id):
    trigger = all_triggers[t_id]
    trigger.stop()

    app_log.warning(f"Stopped trigger with id: {t_id}")


# if __name__ == "__main__":
#     trigger_id = start_triggers()

#     print(f"Gonna do doo dee la di doo for {SLEEP} seconds")
#     time.sleep(SLEEP)

#     stop_triggers(trigger_id)
