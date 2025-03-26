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

import json
import os
import tempfile

from covalent_dispatcher._core.data_modules.utils import run_in_executor
from covalent_dispatcher._dal.base import workflow_db
from covalent_dispatcher._dal.dispatcher_state import TaskGroupState, WorkflowState
from covalent_dispatcher._db.datastore import DataStore


class _WorkflowRunState:

    def __init__(self, db: DataStore):
        self.db = db

    def _get_unresolved(self, dispatch_id: str):
        with self.db.session() as session:
            records = WorkflowState.get(
                session,
                fields=["num_unresolved_tasks"],
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            return records[0].num_unresolved_tasks

    async def get_unresolved(self, dispatch_id: str):
        return await run_in_executor(self._get_unresolved, dispatch_id)

    def _set_unresolved(self, dispatch_id: str, val: int):
        with self.db.session() as session:
            WorkflowState.create(
                session,
                insert_kwargs={
                    "dispatch_id": dispatch_id,
                    "num_unresolved_tasks": val,
                },
            )
            session.commit()

    async def set_unresolved(self, dispatch_id: str, val: int):
        return await run_in_executor(self._set_unresolved, dispatch_id, val)

    def _increment(self, dispatch_id: str, interval: int = 1):
        with self.db.session() as session:
            WorkflowState.incr_bulk(
                session=session,
                increments={"num_unresolved_tasks": interval},
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            records = WorkflowState.get(
                session,
                fields=["num_unresolved_tasks"],
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            session.commit()
            return records[0].num_unresolved_tasks

    async def increment(self, dispatch_id: str, interval: int = 1):
        return await run_in_executor(self._increment, dispatch_id, interval)

    def _decrement(self, dispatch_id: str):
        with self.db.session() as session:
            WorkflowState.incr_bulk(
                session=session,
                increments={"num_unresolved_tasks": -1},
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            records = WorkflowState.get(
                session,
                fields=["num_unresolved_tasks"],
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            session.commit()
            return records[0].num_unresolved_tasks

    async def decrement(self, dispatch_id: str):
        return await run_in_executor(self._decrement, dispatch_id)

    def _remove(self, dispatch_id: str):
        with self.db.session() as session:
            WorkflowState.delete_bulk(
                session=session,
                equality_filters={"dispatch_id": dispatch_id},
                membership_filters={},
            )
            session.commit()

    async def remove(self, dispatch_id: str):
        await run_in_executor(self._remove, dispatch_id)


class TaskGroupRunState:

    def __init__(self, db):
        self.db = db

    def _get_pending(self, dispatch_id: str, task_group_id: int):
        with self.db.session() as session:
            records = TaskGroupState.get(
                session=session,
                fields=["num_pending_parents"],
                equality_filters={"dispatch_id": dispatch_id, "task_group_id": task_group_id},
                membership_filters={},
            )
            return records[0].num_pending_parents

    async def get_pending(self, dispatch_id: str, task_group_id: int):
        return await run_in_executor(self._get_pending, dispatch_id, task_group_id)

    def _set(self, dispatch_id: str, task_group_id: int, num_pending: int, sorted_nodes):
        with self.db.session() as session:
            TaskGroupState.create(
                session=session,
                insert_kwargs={
                    "dispatch_id": dispatch_id,
                    "task_group_id": task_group_id,
                    "num_pending_parents": num_pending,
                    "sorted_tasks": json.dumps(sorted_nodes),
                },
            )
            session.commit()

    async def set(self, dispatch_id: str, task_group_id: int, num_pending: int, sorted_nodes):
        return await run_in_executor(
            self._set, dispatch_id, task_group_id, num_pending, sorted_nodes
        )

    def _decrement(self, dispatch_id: str, task_group_id):
        with self.db.session() as session:
            TaskGroupState.incr_bulk(
                session=session,
                increments={"num_pending_parents": -1},
                equality_filters={"dispatch_id": dispatch_id, "task_group_id": task_group_id},
                membership_filters={},
            )
            records = TaskGroupState.get(
                session,
                fields=["num_pending_parents"],
                equality_filters={"dispatch_id": dispatch_id, "task_group_id": task_group_id},
                membership_filters={},
            )
            session.commit()
            return records[0].num_pending_parents

    async def decrement(self, dispatch_id: str, task_group_id: int):
        return await run_in_executor(self._decrement, dispatch_id, task_group_id)

    async def remove(self, dispatch_id: str, task_group_id: int):
        pass

    def _get_task_group(self, dispatch_id: str, task_group_id: int):
        with self.db.session() as session:
            records = TaskGroupState.get(
                session=session,
                fields=["sorted_tasks"],
                equality_filters={"dispatch_id": dispatch_id, "task_group_id": task_group_id},
                membership_filters={},
            )
            return json.loads(records[0].sorted_tasks)

    async def get_task_group(self, dispatch_id: str, task_group_id: int):
        return await run_in_executor(self._get_task_group, dispatch_id, task_group_id)

    def _remove(self, dispatch_id: str, task_group_id: int):
        with self.db.session() as session:
            TaskGroupState.delete_bulk(
                session=session,
                equality_filters={"dispatch_id": dispatch_id, "task_group_id": task_group_id},
                membership_filters={},
            )
            session.commit()

    async def remove(self, dispatch_id: str, task_group_id: int):
        await run_in_executor(self._remove, dispatch_id, task_group_id)


# Default to tmpfs backed file
cache_db_file = tempfile.NamedTemporaryFile(
    mode="w+b", prefix="covalent-dispatcher-cache-", suffix=".db"
)
cache_db_URL = os.environ.get("COVALENT_CACHE_DB_URL", f"sqlite+pysqlite:///{cache_db_file.name}")
initialize_db = True

# If we want to store dispatcher state in the main DB, let the alembic migrations
# create the tables
if cache_db_URL == workflow_db.db_URL:
    initialize_db = False

cache_db = DataStore(db_URL=cache_db_URL, initialize_db=initialize_db)

_task_group_cache = TaskGroupRunState(db=cache_db)
_workflow_run_cache = _WorkflowRunState(db=cache_db)
