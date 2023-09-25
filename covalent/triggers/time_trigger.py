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
