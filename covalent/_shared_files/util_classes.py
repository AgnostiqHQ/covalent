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
from datetime import datetime
import time
from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class Status:
    STATUS: str

    def __bool__(self):
        """
        Return True if the status is not "NEW_OBJECT"
        """

        return self.STATUS != "NEW_OBJECT"

    def __str__(self) -> str:
        return self.STATUS


class RESULT_STATUS:
    NEW_OBJECT = Status("NEW_OBJECT")
    COMPLETED = Status("COMPLETED")
    FAILED = Status("FAILED")
    RUNNING = Status("RUNNING")
    CANCELLED = Status("CANCELLED")


class DispatchInfo(NamedTuple):
    """
    Information about a dispatch to be shared to a task post dispatch.

    Attributes:
        dispatch_id: Dispatch id of the dispatch.
    """

    dispatch_id: str


class TimerError(Exception):
    """A custom exception used to report errors in usage of the Timer class"""


class Timer:
    """
    Information on execution times of the API function calls when a workflow is dispatched

    Attributes:
        endpoint: The name of an endpoint or function call
        descriptor : A brief description of an action e.g., Updating a workflow
        service: The name of the service e.g. DISPATCHER,
        dispatch_id: The uuid of a dispatch
    """
    DATA = 'Data Service'
    DISPATCHER = 'Dispatcher Service'
    QUEUER = 'Queuer Service'
    QUEUE_CONSUMER = 'Queue Consumer Service'
    RESULTS = 'Results Service'
    RUNNER = 'Runner Service'
    UI = 'UI Service'
    NATS_SERVER = 'Nats Service'

    def __init__(self):
        self._start_time = None

    def start(self, endpoint: str, descriptor: str, service: str, dispatch_id=None):
        """Start a new timer"""
        if self._start_time is not None:
            self._start_time = None

        self._start_time = time.perf_counter()
        return f" Dispatch id: {dispatch_id} \nMetadata: {descriptor}  was initiated by {endpoint} in {service} at " \
               f"{datetime.now()} "

    def stop(self, endpoint: str, descriptor: str, service: str, dispatch_id=None):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            self.start(endpoint, descriptor, service, dispatch_id)

        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None
        return f" Dispatch id: {dispatch_id} \nMetadata: {descriptor} was initiated by {endpoint} " \
               f" in {service} and ran in {elapsed_time:0.4f} ms "
