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


def get_qelectron_db_path(dispatch_id: str, task_id: int):
    """
    Return the path to the Qelectron database for a given dispatch_id and task_id.

    WARNING: SHOULD ONLY BE USED FROM THE SAME MACHINE
    AS WHERE THE USER'S TASK FUNCTION IS BEING RUN.
    """

    database = Database()

    db_path = database.get_db_path(dispatch_id=dispatch_id, node_id=task_id)

    if db_path.exists():
        app_log.debug(f"Found qelectron DB for task {task_id}")
        return db_path
    else:
        app_log.debug(f"Qelectron database not found for task {task_id}")
        return None
