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


import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

SLEEP = 5


class DirEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        super().on_modified(event)
        print("File modified")


class DirTrigger:
    def __init__(self, dir_path, event_name=None) -> None:
        self.dir_path = dir_path
        self.event_name = event_name or "modified"

    def start(self):
        event_handler = DirEventHandler()
        self.observer = Observer()
        self.observer.schedule(event_handler, self.dir_path, recursive=True)
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


def start_triggers():
    # do create_task for all the triggers here
    trigger = DirTrigger(dir_path=".")
    trigger.start()

    print(f"Gonna do doo dee la di doo for {SLEEP} seconds")
    time.sleep(SLEEP)
    trigger.stop()


if __name__ == "__main__":
    start_triggers()
