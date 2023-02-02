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

from covalent._shared_files import logger

from .._results_manager import Result

app_log = logger.app_log
log_stack_info = logger.log_stack_info


class BaseTrigger:
    def __init__(self, lattice_dispatch_id: str = None, dispatcher_addr: str = None):
        self.lattice_dispatch_id = lattice_dispatch_id
        self.dispatcher_addr = dispatcher_addr
        self.new_dispatch_ids = []
        self.observe_blocks = True
        self._is_internal = False

    def _get_status(self):
        if self._is_internal:
            from covalent_dispatcher._service.app import get_result

            return asyncio.run_coroutine_threadsafe(
                get_result(self.lattice_dispatch_id, status_only=True),
                asyncio.get_running_loop(),
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
                asyncio.get_running_loop(),
            ).result()

        from .. import redispatch

        return redispatch(self.lattice_dispatch_id, self.dispatcher_addr)

    def trigger(self):

        status = self._get_status()

        if status == str(Result.NEW_OBJ):
            # To continue the pending dispatch
            same_dispatch_id = self._do_redispatch(True)
            app_log.warning(f"Initiating run for pending dispatch_id: {same_dispatch_id}")

        # To run new redispatch
        new_dispatch_id = self._do_redispatch()
        app_log.warning(f"Redispatching, new dispatch_id: {new_dispatch_id}")
        self.new_dispatch_ids.append(new_dispatch_id)

        # app_log.warning(f"File path that triggered this event: {event.src_path}")
