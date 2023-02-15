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

import time
from threading import Event

from .base import BaseTrigger


class TimeTrigger(BaseTrigger):
    """
    Performs a trigger action every `time_gap` seconds.
    Args:
        time_gap: Amount of seconds to wait before doing a trigger action
    Attributes:
        self.time_gap: Amount of seconds to wait before doing a trigger action
        self.stop_flag: Thread safe flag used to check whether the stop condition has been met
    """

    def __init__(
        self,
        time_gap: int,
        lattice_dispatch_id: str = None,
        dispatcher_addr: str = None,
        triggers_server_addr: str = None,
    ):
        super().__init__(lattice_dispatch_id, dispatcher_addr, triggers_server_addr)
        self.time_gap = time_gap
        self.stop_flag = None

    def observe(self) -> None:
        """
        Keep performing the trigger action every `self.time_gap` seconds
        until stop condition has been met.
        """

        # Stopping mechanism for a blocking observe()
        self.stop_flag = Event()
        while not self.stop_flag.is_set():
            time.sleep(self.time_gap)
            self.trigger()

    def stop(self) -> None:
        """
        Stop the running `self.observe()` method by setting the `self.stop_flag` flag.
        """

        self.stop_flag.set()
