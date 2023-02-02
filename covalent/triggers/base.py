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

    def _internal_trigger(self):
        import asyncio

        from covalent_dispatcher import run_dispatcher, run_redispatch
        from covalent_dispatcher._service.app import get_result

        event_loop = asyncio.get_running_loop()

        status = asyncio.run_coroutine_threadsafe(
            get_result(
                self.lattice_dispatch_id, status_only=True, dispatcher_addr=self.dispatcher_addr
            ).result()["status"],
            event_loop,
        ).result()

        if status == str(Result.NEW_OBJ):
            # To continue pending dispatch
            same_dispatch_id = asyncio.run_coroutine_threadsafe(
                run_dispatcher(None, pending_dispatch_id=self.lattice_dispatch_id), event_loop
            ).result()
            app_log.warning(f"Initiating run for same dispatch_id: {same_dispatch_id}")

        else:
            # To run new redispatch
            new_dispatch_id = asyncio.run_coroutine_threadsafe(
                run_redispatch(self.lattice_dispatch_id, None, None, False), event_loop
            ).result()
            app_log.warning(f"Redispatching, new dispatch_id: {new_dispatch_id}")

            self.new_dispatch_ids.append(new_dispatch_id)

    def _remote_trigger(self):
        pass

    def trigger(self):
        if self._is_internal:
            return self._internal_trigger()
        return self._remote_trigger()

        # app_log.warning(f"File path that triggered this event: {event.src_path}")
