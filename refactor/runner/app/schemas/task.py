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

from typing import Any, Callable, Dict, List

from pydantic import BaseModel


class Task(BaseModel):
    task_id: int
    func: Callable
    args: List[Any]
    kwargs: Dict[str, Any]
    executor: Any
    results_dir: str


class TaskPickleList(BaseModel):
    tasks: List[bytes]


class RunTaskResponse(BaseModel):
    left_out_task_ids: List


class CancelResponse(BaseModel):
    cancelled_dispatch_id: str
    cancelled_task_id: str


class TaskStatus(BaseModel):
    status: str
