# Copyright 2021 Agnostiq Inc.
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

"""
Helper classes for the dispatcher
"""

from .store import _DictStore, _KeyValueBase


def _pending_parents_key(dispatch_id: str, node_id: int):
    return f"pending-parents-{dispatch_id}:{node_id}"


def _unresolved_tasks_key(dispatch_id: str):
    return f"unresolved-{dispatch_id}"


def _task_groups_key(dispatch_id: str, task_group_id: int):
    return f"task-groups-{dispatch_id}:{task_group_id}"


class _UnresolvedTasksCache:
    def __init__(self, store: _KeyValueBase = _DictStore()):
        self._store = store

    async def get_unresolved(self, dispatch_id: str):
        key = _unresolved_tasks_key(dispatch_id)
        return await self._store.get(key)

    async def set_unresolved(self, dispatch_id: str, val: int):
        key = _unresolved_tasks_key(dispatch_id)
        await self._store.insert(key, val)

    async def increment(self, dispatch_id: str, interval: int = 1):
        key = _unresolved_tasks_key(dispatch_id)
        return await self._store.increment(key, interval)

    async def decrement(self, dispatch_id: str):
        key = _unresolved_tasks_key(dispatch_id)
        return await self._store.increment(key, -1)

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
        key = _pending_parents_key(dispatch_id, task_group_id)
        return await self._store.increment(key, -1)

    async def remove(self, dispatch_id: str, task_group_id: int):
        key = _pending_parents_key(dispatch_id, task_group_id)
        await self._store.remove(key)


class _SortedTaskGroups:
    def __init__(self, store: _KeyValueBase = _DictStore()):
        self._store = store

    async def get_task_group(self, dispatch_id: str, task_group_id: int):
        key = _task_groups_key(dispatch_id, task_group_id)
        return await self._store.get(key)

    async def set_task_group(self, dispatch_id: str, task_group_id: int, sorted_nodes: list):
        key = _task_groups_key(dispatch_id, task_group_id)
        await self._store.insert(key, sorted_nodes)

    async def remove(self, dispatch_id: str, task_group_id: int):
        key = _task_groups_key(dispatch_id, task_group_id)
        await self._store.remove(key)


_pending_parents = _PendingParentsCache()
_unresolved_tasks = _UnresolvedTasksCache()
_sorted_task_groups = _SortedTaskGroups()
