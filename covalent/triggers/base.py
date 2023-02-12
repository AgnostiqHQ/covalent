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
import json
from abc import abstractmethod

import requests

from .._results_manager import Result
from .._shared_files import logger
from .._shared_files.config import get_config
from .._shared_files.util_classes import Status

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class BaseTrigger:
    """
    Base class to be subclassed by any custom defined trigger.
    Implements all the necessary methods used for interacting with dispatches, including
    getting their statuses and performing a redispatch of them whenever the trigger gets triggered.

    Args:
        lattice_dispatch_id: Dispatch ID of the worfklow which has to be redispatched in case this trigger gets triggered
        dispatcher_addr: Address of dispatcher server used to retrieve info about or redispatch any dispatches
        triggers_server_addr: Address of the Triggers server (if there is any) to register this trigger to,
                              uses the dispatcher's address by default

    Attributes:
        self.lattice_dispatch_id: Dispatch ID of the worfklow which has to be redispatched in case this trigger gets triggered
        self.dispatcher_addr: Address of dispatcher server used to retrieve info about or redispatch any dispatches
        self.triggers_server_addr: Address of the Triggers server (if there is any) to register this trigger to,
                              uses the dispatcher's address by default
        self.new_dispatch_ids: List of all the newly created dispatch ids from performing redispatch
        self.observe_blocks: Boolean to indicate whether the `self.observe` method is a blocking call
        self.event_loop: Event loop to be used if directly calling dispatcher's functions instead of the REST APIs
        self.use_internal_funcs: Boolean indicating whether to use dispatcher's functions directly instead of through API calls
        self.stop_flag: To handle stopping mechanism in a thread safe manner in case `self.observe()` is a blocking call (e.g. see TimeTrigger)
    """

    def __init__(
        self,
        lattice_dispatch_id: str = None,
        dispatcher_addr: str = None,
        triggers_server_addr: str = None,
    ):
        self.lattice_dispatch_id = lattice_dispatch_id
        self.dispatcher_addr = dispatcher_addr
        self.triggers_server_addr = triggers_server_addr
        self.new_dispatch_ids = []
        self.observe_blocks = True
        self.event_loop = (
            None  # to attach the event loop when directly using dispatcher's functions
        )
        self.use_internal_funcs = (
            True  # whether to use dispatcher's functions directly instead of through API calls
        )
        self.stop_flag = None  # to handle stopping mechanism in a thread safe manner in case observe() is a blocking call (e.g. see TimeTrigger)

    def register(self) -> None:
        """
        Register this trigger to the Triggers server and start observing.
        """
        self._register(self.to_dict(), self.triggers_server_addr)

    @staticmethod
    def _register(trigger_data, triggers_server_addr=None) -> None:
        """
        Register a trigger to the Triggers server given only its dictionary format and start observing.
        Args:
        trigger_data: Dictionary representation of a trigger
        """
        if triggers_server_addr is None:
            triggers_server_addr = (
                get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
            )
        register_trigger_url = f"http://{triggers_server_addr}/api/triggers/register"

        r = requests.post(register_trigger_url, json=trigger_data)
        r.raise_for_status()

    def _get_status(self) -> Status:
        """
        Get status about the connected dispatch id to check whether its a pending
        dispatch or new redispatch has to be made.
        Returns:
            status: Status
        """

        if self.use_internal_funcs:
            from covalent_dispatcher._service.app import get_result

            response = asyncio.run_coroutine_threadsafe(
                get_result(self.lattice_dispatch_id, status_only=True),
                self.event_loop,
            ).result()

            if isinstance(response, dict):
                return response["status"]

            return json.loads(response.body.decode()).get("status")

        from .. import get_result

        return get_result(
            self.lattice_dispatch_id, status_only=True, dispatcher_addr=self.dispatcher_addr
        )["status"]

    def _do_redispatch(self, is_pending: bool = False) -> str:
        """
        Perform a redispatch of the connected dispatch id and return a new one.
        Args:
            is_pending: Whether the connected dispatch id is pending
        Returns:
            new_dispatch_id: Dispatch id of the newly dispatched workflow
        """

        if self.use_internal_funcs:
            from covalent_dispatcher import run_redispatch

            return asyncio.run_coroutine_threadsafe(
                run_redispatch(self.lattice_dispatch_id, None, None, False, is_pending),
                self.event_loop,
            ).result()

        from .. import redispatch

        return redispatch(self.lattice_dispatch_id, self.dispatcher_addr, is_pending)()

    def trigger(self) -> None:
        """
        Trigger this trigger and perform a redispatch of the connected dispatch id's workflow.
        Should be called within `self.observe()` whenever a trigger action is desired.
        Raises:
            RuntimeError: In case no dispatch id is connected to this trigger
        """

        if not self.lattice_dispatch_id:
            raise RuntimeError(
                "`lattice_dispatch_id` is None. Please attach this trigger to a lattice before triggering."
            )

        status = self._get_status()

        if status == str(Result.NEW_OBJ) or status is None:
            # To continue the pending dispatch
            same_dispatch_id = self._do_redispatch(True)
            app_log.debug(f"Initiating run for pending dispatch_id: {same_dispatch_id}")
        else:
            # To run new redispatch
            new_dispatch_id = self._do_redispatch()
            app_log.debug(f"Redispatching, new dispatch_id: {new_dispatch_id}")
            self.new_dispatch_ids.append(new_dispatch_id)

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of this trigger which can later be used to regenerate it.
        Returns:
            tr_dict: Dictionary representation of this trigger
        """

        tr_dict = self.__dict__.copy()
        tr_dict["name"] = str(self.__class__.__name__)
        return tr_dict

    @abstractmethod
    def observe(self):
        """
        Start observing for any change which can be used to trigger this trigger.
        To be implemented by the subclass.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop observing for changes.
        To be implemented by the subclass.
        """
        pass
