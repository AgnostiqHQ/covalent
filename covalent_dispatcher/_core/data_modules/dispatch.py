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

"""
Queries involving dispatches
"""

from typing import Dict, List

from ..._dal.result import get_result_object
from .utils import run_in_executor


def get_sync(dispatch_id: str, keys: List[str]) -> Dict:
    refresh = False
    result_object = get_result_object(dispatch_id)
    return result_object.get_values(keys, refresh=refresh)


async def get(dispatch_id: str, keys: List[str]) -> Dict:
    return await run_in_executor(
        get_sync,
        dispatch_id,
        keys,
    )


def get_incomplete_tasks_sync(dispatch_id: str) -> Dict:
    """Query all cancelled or failed tasks"""
    result_object = get_result_object(dispatch_id, False)
    refresh = False
    return result_object._get_incomplete_nodes(refresh)


async def get_incomplete_tasks(dispatch_id: str) -> Dict:
    """Query all cancelled or failed tasks in a dispatch.

    Args:
        dispatch_id: The id of the dispatch

    Returns:
        {"cancelled": [node_ids], "failed": [node_ids]}
    """

    return await run_in_executor(get_incomplete_tasks_sync, dispatch_id)


def update_sync(dispatch_id, dispatch_result):
    result_object = get_result_object(dispatch_id)
    result_object._update_dispatch(**dispatch_result)


async def update(dispatch_id, dispatch_result):
    await run_in_executor(update_sync, dispatch_id, dispatch_result)
