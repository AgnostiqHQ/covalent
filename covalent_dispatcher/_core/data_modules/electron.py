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
Utilities for querying the transport graph
"""

from typing import Dict, List

from ..._dal.result import get_result_object
from .utils import run_in_executor


def get_bulk_sync(dispatch_id: str, node_ids: List[int], keys: List[str]) -> List[Dict]:
    result_object = get_result_object(dispatch_id)
    attrs = result_object.lattice.transport_graph.get_values_for_nodes(
        node_ids=node_ids,
        keys=keys,
        refresh=False,
    )
    return attrs


async def get_bulk(dispatch_id: str, node_ids: List[int], keys: List[str]) -> List[Dict]:
    """Query attributes for multiple electrons.

    Args:
        node_ids: The list of nodes to query
        keys: The list of attributes to query for each electron

    Returns:
        A list of dictionaries {attr_key: attr_val}, one for
        each node id, in the same order as `node_ids`

    Example:
    ```
        await get_bulk(
            "my_dispatch", [2, 4], ["name", "status"],
        )
    ```
    will return
    ```
    [
        {
            "name": "task_2", "status": RESULT_STATUS.COMPLETED,
        },
        {
            "name": "task_4, "status": RESULT_STATUS.FAILED,
        },
    ]
    ```

    """
    return await run_in_executor(
        get_bulk_sync,
        dispatch_id,
        node_ids,
        keys,
    )


async def get(dispatch_id: str, node_id: int, keys: List[str]) -> Dict:
    """Convenience function to query attributes for an electron.

    Args:
        node_id: The node to query
        keys: The list of attributes to query

    Returns:
        A dictionary {attr_key: attr_val}

    Example:
    ```
        await get(
            "my_dispatch", 2, ["name", "status"],
        )
    ```
    will return
    ```
        {
            "name": "task_2", "status": RESULT_STATUS.COMPLETED,
        }
    ```

    """
    attrs = await get_bulk(dispatch_id, [node_id], keys)
    return attrs[0]


def update_sync(dispatch_id: str, node_result: Dict):
    result_object = get_result_object(dispatch_id, bare=True)
    return result_object._update_node(**node_result)


async def update(dispatch_id: str, node_result: Dict):
    """Update a node's attributes"""
    return await run_in_executor(update_sync, dispatch_id, node_result)
