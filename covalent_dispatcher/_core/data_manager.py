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
Defines the core functionality of the result service
"""

import asyncio
import uuid

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._workflow.lattice import Lattice

from .._db import update, upsert
from .._db.write_result_to_db import resolve_electron_id

app_log = logger.app_log
log_stack_info = logger.log_stack_info

# References to result objects of live dispatches
_registered_dispatches = {}

# Map of dispatch_id -> message_queue for pushing node status updates
# to dispatcher
_dispatch_status_queues = {}


def generate_node_result(
    node_id,
    start_time=None,
    end_time=None,
    status=None,
    output=None,
    error=None,
    stdout=None,
    stderr=None,
    sub_dispatch_id=None,
    sublattice_result=None,
):

    return {
        "node_id": node_id,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "output": output,
        "error": error,
        "stdout": stdout,
        "stderr": stderr,
        "sub_dispatch_id": sub_dispatch_id,
        "sublattice_result": sublattice_result,
    }


# Domain: result
async def update_node_result(result_object, node_result):
    app_log.warning("Updating node result (run_planned_workflow).")
    try:
        update._node(result_object, **node_result)
    except Exception as ex:
        app_log.exception("Error persisting node update: {ex}")
        node_result["status"] = Result.FAILED
    finally:
        node_id = node_result["node_id"]
        node_status = node_result["status"]
        dispatch_id = result_object.dispatch_id
        if node_status:
            status_queue = get_status_queue(dispatch_id)
            await status_queue.put((node_id, node_status))


# Domain: result
def initialize_result_object(
    json_lattice: str,
    parent_result_object: Result = None,
    parent_electron_id: int = None,
    assigned_dispatch_id: str = None,
) -> Result:
    """Convenience function for constructing a result object from a json-serialized lattice.

    Args:
        json_lattice: a JSON-serialized lattice
        parent_result_object: the parent result object if json_lattice is a sublattice
        parent_electron_id: the DB id of the parent electron (for sublattices)

    Returns:
        Result: result object
    """

    dispatch_id = assigned_dispatch_id or get_unique_id()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, dispatch_id)
    if parent_result_object:
        result_object._root_dispatch_id = parent_result_object._root_dispatch_id

    result_object._electron_id = parent_electron_id
    result_object._initialize_nodes()
    app_log.debug("2: Constructed result object and initialized nodes.")

    update.persist(result_object, electron_id=parent_electron_id)
    app_log.debug("Result object persisted.")

    return result_object


# Domain: result
def get_unique_id() -> str:
    """
    Get a unique ID.

    Args:
        None

    Returns:
        str: Unique ID
    """

    return str(uuid.uuid4())


def make_dispatch(
    json_lattice: str,
    parent_result_object: Result = None,
    parent_electron_id: int = None,
    assigned_dispatch_id: str = None,
) -> Result:

    result_object = initialize_result_object(
        json_lattice, parent_result_object, parent_electron_id, assigned_dispatch_id
    )
    _register_result_object(result_object)
    return result_object.dispatch_id


def get_result_object(dispatch_id: str) -> Result:
    return _registered_dispatches[dispatch_id]


def _register_result_object(result_object: Result):
    dispatch_id = result_object.dispatch_id
    _registered_dispatches[dispatch_id] = result_object
    _dispatch_status_queues[dispatch_id] = asyncio.Queue()


def finalize_dispatch(dispatch_id: str):
    del _dispatch_status_queues[dispatch_id]
    del _registered_dispatches[dispatch_id]


def get_status_queue(dispatch_id: str):
    return _dispatch_status_queues[dispatch_id]


async def persist_result(dispatch_id: str):
    result_object = get_result_object(dispatch_id)
    update.persist(result_object)
    await _update_parent_electron(result_object)


async def _update_parent_electron(result_object: Result):
    parent_eid = result_object._electron_id

    if parent_eid:
        dispatch_id, node_id = resolve_electron_id(parent_eid)
        status = result_object.status
        if status == Result.POSTPROCESSING_FAILED:
            status = Result.FAILED
        node_result = generate_node_result(
            node_id=node_id,
            end_time=result_object.end_time,
            status=status,
            output=result_object._result,
            error=result_object._error,
            sublattice_result=result_object,
        )
        parent_result_obj = get_result_object(dispatch_id)
        app_log.debug(f"Updating sublattice parent node {dispatch_id}:{node_id}")
        await update_node_result(parent_result_obj, node_result)


def upsert_lattice_data(dispatch_id: str):
    result_object = get_result_object(dispatch_id)
    upsert._lattice_data(result_object)
