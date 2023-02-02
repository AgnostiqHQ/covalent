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
from abc import abstractmethod

import requests

from .._results_manager import Result
from .._shared_files import logger
from .._shared_files.config import get_config

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class BaseTrigger:
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
        self.event_loop = None

        self._is_internal = False

    def register(self):
        self._register(self.to_dict(), self.triggers_server_addr)

    @staticmethod
    def _register(trigger_data, triggers_server_addr=None):
        if triggers_server_addr is None:
            triggers_server_addr = (
                get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
            )
        register_trigger_url = f"http://{triggers_server_addr}/api/triggers/register"

        r = requests.post(register_trigger_url, json=trigger_data)
        r.raise_for_status()

    def _get_status(self):
        if self._is_internal:
            from covalent_dispatcher._service.app import get_result

            return asyncio.run_coroutine_threadsafe(
                get_result(self.lattice_dispatch_id, status_only=True),
                self.event_loop,
            ).result()["status"]

        from .. import get_result

        return get_result(
            self.lattice_dispatch_id, status_only=True, dispatcher_addr=self.dispatcher_addr
        )["status"]

    def _do_redispatch(self, is_pending: bool = False):
        if self._is_internal:
            from covalent_dispatcher import run_redispatch

            return asyncio.run_coroutine_threadsafe(
                run_redispatch(self.lattice_dispatch_id, None, None, False, is_pending),
                self.event_loop,
            ).result()

        from .. import redispatch

        return redispatch(self.lattice_dispatch_id, self.dispatcher_addr)()

    def trigger(self):

        if not self.lattice_dispatch_id:
            raise RuntimeError(
                "`lattice_dispatch_id` is None. Please attach this trigger to a lattice before triggering."
            )

        status = self._get_status()

        if status == str(Result.NEW_OBJ):
            # To continue the pending dispatch
            same_dispatch_id = self._do_redispatch(True)
            app_log.warning(f"Initiating run for pending dispatch_id: {same_dispatch_id}")
        else:
            # To run new redispatch
            new_dispatch_id = self._do_redispatch()
            app_log.warning(f"Redispatching, new dispatch_id: {new_dispatch_id}")
            self.new_dispatch_ids.append(new_dispatch_id)

    def to_dict(self):
        tr_dict = self.__dict__.copy()
        tr_dict["name"] = str(self.__class__.__name__)
        return tr_dict

    @abstractmethod
    def observe(self):
        pass

    @abstractmethod
    def stop(self):
        pass
