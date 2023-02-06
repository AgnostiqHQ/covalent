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

"""
Helper classes for the dispatcher
"""

from .store import _DictStore, _KeyValueBase


def _pending_parents_key(dispatch_id: str, node_id: int):
    return f"{dispatch_id}:{node_id}"


def _unresolved_tasks_key(dispatch_id: str):
    return dispatch_id


def _task_groups_key(dispatch_id: str, task_group_id: int):
    return _pending_parents_key(dispatch_id, task_group_id)


class _UnresolvedTasksCache:
    def __init__(self, store: _KeyValueBase = _DictStore()):
        self._store = store

    async def get_unresolved(self, dispatch_id: str):
        key = _unresolved_tasks_key(dispatch_id)
        return await self._store.get(key)

    async def set_unresolved(self, dispatch_id: str, val: int):
        key = _unresolved_tasks_key(dispatch_id)
        await self._store.insert(key, val)

    async def increment(self, dispatch_id: str):
        current = await self.get_unresolved(dispatch_id)
        await self.set_unresolved(dispatch_id, current + 1)

    async def decrement(self, dispatch_id: str):
        current = await self.get_unresolved(dispatch_id)
        await self.set_unresolved(dispatch_id, current - 1)

    async def remove(self, dispatch_id: str):
        key = _unresolved_tasks_key(dispatch_id)
        await self._store.remove(key)


class _PendingParentsCache:
    def __init__(self, store: _KeyValueBase = _DictStore()):
        self._store = store

    async def get_pending(self, dispatch_id: str, task_group_id: int):
        key = _pending_parents_key(dispatch_id, task_group_id)
        return await self._store.get(key)

    async def set_pending(self, dispatch_id: str, task_group_id: int, val: int):
        key = _pending_parents_key(dispatch_id, task_group_id)
        await self._store.insert(key, val)

    async def decrement(self, dispatch_id: str, task_group_id: int):
        current = await self.get_pending(dispatch_id, task_group_id)
        await self.set_pending(dispatch_id, task_group_id, current - 1)

    async def remove(self, dispatch_id: str, task_group_id: int):
        key = _pending_parents_key(dispatch_id, task_group_id)
        await self._store.remove(key)


class _SortedTaskGroups:
    def __init__(self, store: _KeyValueBase = _DictStore()):
        self._store = store

    async def get_task_group(self, dispatch_id: str, task_group_id: int):
        key = _task_groups_key(dispatch_id, task_group_id)
        await self._store.get(key)

    async def set_task_group(self, dispatch_id: str, task_group_id: int, sorted_nodes: list):
        key = _task_groups_key(dispatch_id, task_group_id)
        await self._store.insert(key, sorted_nodes)

    async def remove(self, dispatch_id: str, task_group_id: int):
        key = _task_groups_key(dispatch_id, task_group_id)
        await self._store.remove(key)


_pending_parents = _PendingParentsCache()
_unresolved_tasks = _UnresolvedTasksCache()
_sorted_task_groups = _SortedTaskGroups()
