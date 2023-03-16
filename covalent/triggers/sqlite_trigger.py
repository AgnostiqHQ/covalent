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

import sqlite3
import time
from threading import Event

from covalent._shared_files import logger

from .base import BaseTrigger

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class SQLiteTrigger(BaseTrigger):
    """
    SQLite Trigger which can read for new row additions

    """

    def __init__(
        self,
        db_path: str,
        table_name: str,
        lattice_dispatch_id: str = None,
        dispatcher_addr: str = None,
        triggers_server_addr: str = None,
    ):
        super().__init__(lattice_dispatch_id, dispatcher_addr, triggers_server_addr)

        self.stop_flag = None
        self.last_id = 1
        self.initial_status = "pending"

        self.db_path = db_path
        self.table_name = table_name

    def observe(self) -> None:
        """
        Keep performing the trigger action whenever ...
        until stop condition has been met.
        """

        app_log.warning("Inside SQLiteTrigger's observe")

        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()

        self.stop_flag = Event()
        while not self.stop_flag.is_set():
            # Check if there are any new rows in the database
            cursor.execute(
                f"SELECT COUNT(*) FROM {self.table_name} WHERE id > ? AND status = ?",
                (self.last_id, self.initial_status),
            )
            count = cursor.fetchone()[0]
            app_log.warning(f"Count: {count}, last id: {self.last_id}")

            if count > 0:
                # Get the newest row in the database
                cursor.execute(
                    f"SELECT id FROM {self.table_name} WHERE id > ? AND status = ?",
                    (self.last_id, self.initial_status),
                )

                ids = cursor.fetchall()

                app_log.warning(f"IDs which are triggering: {ids}")

                # Trigger the workflow for all the pending ids
                for _ in ids:
                    self.trigger()

                # Update the last_id to the newest row id
                self.last_id = ids[-1][0]

            time.sleep(1)

        cursor.close()
        connection.close()

    def stop(self) -> None:
        """
        Stop the running `self.observe()` method by setting the `self.stop_flag` flag.
        """

        self.stop_flag.set()
