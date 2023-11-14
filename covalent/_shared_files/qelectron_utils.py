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


from covalent.quantum.qserver.database import Database

from .logger import app_log


def get_qelectron_db_dict(dispatch_id: str, task_id: int, exists_only: bool = False):
    """
    Return the Qelectron database as a dictionary
    for a given dispatch_id and task_id.

    """

    try:
        database = Database()

        if exists_only:
            return database.db_exists(dispatch_id=dispatch_id, node_id=task_id)

        res = database.get_db_dict(dispatch_id=dispatch_id, node_id=task_id)

        app_log.error(f"Found qelectron DB for task {task_id}")
        # app_log.error(f"Qelectron DB: {res}")
        return res

    except FileNotFoundError:
        app_log.error(f"Qelectron database not found for task {task_id}")
        return {}
