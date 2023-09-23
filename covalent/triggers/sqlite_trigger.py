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

import sqlite3
import time
from functools import partial
from threading import Event
from typing import List

from covalent._shared_files import logger

from .base import BaseTrigger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class SQLiteTrigger(BaseTrigger):
    """
    SQLite based Trigger which can read for changes in a SQLite database
    and trigger workflows based on that.

    Args:
        db_path: Absolute path to the database file
        table_name: Name of the table to observe
        poll_interval: Time in seconds to wait for before reading the database again
        where_clauses: List of "WHERE" conditions, e.g. ["id > 2", "status = pending"], to check when
                       polling the database
        trigger_after_n: Number of times the event must happen after which the workflow will be triggered.
                         e.g value of 2 means workflow will be triggered once the event has occurred twice.
        lattice_dispatch_id: Lattice dispatch id of the workflow to be triggered
        dispatcher_addr: Address of the dispatcher server
        triggers_server_addr: Address of the triggers server

    Attributes:
        self.db_path: Absolute path to the database file
        self.table_name: Name of the table to observe
        self.poll_interval: Time in seconds to wait for before reading the database again
        self.where_clauses: List of "WHERE" conditions, e.g. ["id > 2", "status = pending"], to check when
                            polling the database
        self.trigger_after_n: Number of times the event must happen after which the workflow will be triggered.
                              e.g value of 2 means workflow will be triggered once the event has occurred twice.
        self.stop_flag: Thread safe flag used to check whether the stop condition has been met

    """

    def __init__(
        self,
        db_path: str,
        table_name: str,
        poll_interval: int = 1,
        where_clauses: List[str] = None,
        trigger_after_n: int = 1,
        lattice_dispatch_id: str = None,
        dispatcher_addr: str = None,
        triggers_server_addr: str = None,
    ):
        super().__init__(lattice_dispatch_id, dispatcher_addr, triggers_server_addr)

        self.db_path = db_path
        self.table_name = table_name
        self.poll_interval = poll_interval

        self.where_clauses = where_clauses

        self.trigger_after_n = trigger_after_n

        self.stop_flag = None

    def observe(self) -> None:
        """
        Keep performing the trigger action as long as
        where conditions are met or until stop has being called
        """

        app_log.debug("Inside SQLiteTrigger's observe")
        event_count = 0

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        sql_poll_cmd = f"SELECT * FROM {self.table_name}"

        if self.where_clauses:
            sql_poll_cmd += " WHERE "
            sql_poll_cmd += " AND ".join(list(self.where_clauses))

        execute_cmd = partial(cursor.execute, sql_poll_cmd)

        self.stop_flag = Event()
        while not self.stop_flag.is_set():
            # Read the DB with specified command
            try:
                execute_cmd()
            except sqlite3.OperationalError:
                time.sleep(self.poll_interval)
                continue

            # If command ran successfuly, trigger the workflow
            if selected_rows := cursor.fetchall():
                event_count += 1
                if event_count == self.trigger_after_n:
                    self.trigger()
                    event_count = 0

            time.sleep(self.poll_interval)

        cursor.close()
        connection.close()

    def stop(self) -> None:
        """
        Stop the running `self.observe()` method by setting the `self.stop_flag` flag.
        """

        self.stop_flag.set()
