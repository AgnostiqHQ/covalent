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
Defines the core functionality of the result service
"""

import asyncio
import traceback
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, Optional

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.defaults import sublattice_prefix
from covalent._shared_files.qelectron_utils import extract_qelectron_db, write_qelectron_db
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport_graph_ops import TransportGraphOps

from .._db import load, update, upsert
from .._db.write_result_to_db import resolve_electron_id

app_log = logger.app_log
log_stack_info = logger.log_stack_info

# References to result objects of live dispatches
_registered_dispatches = {}

# Map of dispatch_id -> message_queue for pushing node status updates
# to dispatcher
_dispatch_status_queues = {}


def generate_node_result(
    dispatch_id: str,
    node_id: int,
    node_name: str,
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
    """
    Helper routine to prepare the node result

    Arg(s)
        dispatch_id: ID of the dispatched workflow
        node_id: ID of the node in the trasport graph
        node_name: Name of the node
        start_time: Start time of the node
        end_time: Time at which the node finished executing
        status: Status of the node's execution
        output: Output of the node
        error: Error from the node
        stdout: STDOUT of a node
        stderr: STDERR generated during node execution
        sub_dispatch_id: Dispatch ID of the sublattice
        sublattice_result: Result of the sublattice

    Return(s)
        Dictionary of the inputs
    """
    clean_stdout, bytes_data = extract_qelectron_db(stdout)
    qelectron_data_exists = bool(bytes_data)

    if qelectron_data_exists:
        app_log.debug(f"Reproducing Qelectron database for node {node_id}")
        write_qelectron_db(dispatch_id, node_id, bytes_data)

    return {
        "node_id": node_id,
        "node_name": node_name,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "output": output,
        "error": error,
        "stdout": clean_stdout,
        "stderr": stderr,
        "sub_dispatch_id": sub_dispatch_id,
        "sublattice_result": sublattice_result,
        "qelectron_data_exists": qelectron_data_exists,
    }


async def _handle_built_sublattice(dispatch_id: str, node_result: Dict) -> None:
    """Make dispatch for sublattice node.

    Note: The status COMPLETED which invokes this function refers to the graph being built. Once this step is completed, the sublattice is ready to be dispatched. Hence, the status is changed to DISPATCHING.

    Args:
        dispatch_id: Dispatch ID
        node_result: Node result dictionary

    """
    try:
        node_result["status"] = RESULT_STATUS.DISPATCHING_SUBLATTICE
        result_object = get_result_object(dispatch_id)
        sub_dispatch_id = await make_sublattice_dispatch(result_object, node_result)
        node_result["sub_dispatch_id"] = sub_dispatch_id
        node_result["start_time"] = datetime.now(timezone.utc)
        node_result["end_time"] = None
    except Exception as ex:
        tb = "".join(traceback.TracebackException.from_exception(ex).format())
        node_result["status"] = RESULT_STATUS.FAILED
        node_result["error"] = tb
        app_log.debug(f"Failed to make sublattice dispatch: {tb}")


# Domain: result
async def update_node_result(result_object, node_result) -> None:
    """
    Updates the result object with the current node_result

    Arg(s)
        result_object: Result object the current dispatch
        node_result: Result of the node to be updated in the result object

    Return(s)
        None

    """
    app_log.debug(f"Updating node result for {node_result['node_id']}.")

    if (
        node_result["status"] == RESULT_STATUS.COMPLETED
        and node_result["node_name"].startswith(sublattice_prefix)
        and not node_result["sub_dispatch_id"]
    ):
        app_log.debug(
            f"Sublattice {node_result['node_name']} build graph completed, invoking make sublattice dispatch..."
        )
        await _handle_built_sublattice(result_object.dispatch_id, node_result)

    try:
        update._node(result_object, **node_result)
    except Exception as ex:
        app_log.exception(f"Error persisting node update: {ex}")
        node_result["status"] = RESULT_STATUS.FAILED
    finally:
        sub_dispatch_id = node_result["sub_dispatch_id"]
        detail = {"sub_dispatch_id": sub_dispatch_id} if sub_dispatch_id is not None else {}
        if node_status := node_result["status"]:
            dispatch_id = result_object.dispatch_id
            status_queue = get_status_queue(dispatch_id)
            node_id = node_result["node_id"]
            await status_queue.put((node_id, node_status, detail))


# Domain: result
def initialize_result_object(
    json_lattice: str, parent_result_object: Result = None, parent_electron_id: int = None
) -> Result:
    """Convenience function for constructing a result object from a json-serialized lattice.

    Args:
        json_lattice: a JSON-serialized lattice
        parent_result_object: the parent result object if json_lattice is a sublattice
        parent_electron_id: the DB id of the parent electron (for sublattices)

    Returns:
        Result: result object

    """
    dispatch_id = get_unique_id()
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


async def make_dispatch(
    json_lattice: str, parent_result_object: Result = None, parent_electron_id: int = None
) -> str:
    """Make a dispatch from a json-serialized lattice.

    Args:
        json_lattice: a JSON-serialized lattice.
        parent_result_object: the parent result object if json_lattice is a sublattice.
        parent_electron_id: the DB id of the parent electron (for sublattices).

    Returns:
        Dispatch ID of the lattice.

    """
    result_object = initialize_result_object(
        json_lattice, parent_result_object, parent_electron_id
    )
    _register_result_object(result_object)
    return result_object.dispatch_id


async def make_sublattice_dispatch(result_object: Result, node_result: dict) -> str:
    """Get sublattice json lattice (once the transport graph has been built) and invoke make_dispatch.

    Args:
        result_object: Result object for parent dispatch of the node.
        node_result: Result of the node.

    Returns:
        str: Dispatch ID of the sublattice.

    """
    node_id = node_result["node_id"]
    json_lattice = node_result["output"].object_string
    parent_electron_id = load.electron_record(result_object.dispatch_id, node_id)["id"]
    app_log.debug(
        f"Making sublattice dispatch for node_id {node_id} and electron_id {parent_electron_id}."
    )
    return await make_dispatch(json_lattice, result_object, parent_electron_id)


def _get_result_object_from_new_lattice(
    json_lattice: str, old_result_object: Result, reuse_previous_results: bool
) -> Result:
    """Get new result object for re-dispatching from new lattice json.

    Args:
        json_lattice: JSON-serialized lattice.
        old_result_object: Result object of the previous dispatch.

    Returns:
        Result object.

    """
    lat = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lat, get_unique_id())
    result_object._initialize_nodes()

    if reuse_previous_results:
        tg = result_object.lattice.transport_graph
        tg_old = old_result_object.lattice.transport_graph
        reusable_nodes = TransportGraphOps(tg_old).get_reusable_nodes(tg)
        TransportGraphOps(tg).copy_nodes_from(tg_old, reusable_nodes)

    return result_object


def _get_result_object_from_old_result(
    old_result_object: Result, reuse_previous_results: bool
) -> Result:
    """Get new result object for re-dispatching from old result object.

    Args:
        old_result_object: Result object of the previous dispatch.
        reuse_previous_results: Whether to reuse previous results.

    Returns:
        Result: Result object for the new dispatch.

    """
    result_object = Result(old_result_object.lattice, get_unique_id())
    result_object._num_nodes = old_result_object._num_nodes

    if not reuse_previous_results:
        result_object._initialize_nodes()

    return result_object


def make_derived_dispatch(
    parent_dispatch_id: str,
    json_lattice: Optional[str] = None,
    electron_updates: Optional[Dict[str, Callable]] = None,
    reuse_previous_results: bool = False,
) -> str:
    """Make a re-dispatch from a previous dispatch.

    Args:
        parent_dispatch_id: Dispatch ID of the parent dispatch.
        json_lattice: JSON-serialized lattice of the new dispatch.
        electron_updates: Dictionary of electron updates.
        reuse_previous_results: Whether to reuse previous results.

    Returns:
        str: Dispatch ID of the new dispatch.

    """
    if electron_updates is None:
        electron_updates = {}

    old_result_object = load.get_result_object_from_storage(parent_dispatch_id)

    if json_lattice:
        result_object = _get_result_object_from_new_lattice(
            json_lattice, old_result_object, reuse_previous_results
        )
    else:
        result_object = _get_result_object_from_old_result(
            old_result_object, reuse_previous_results
        )

    result_object.lattice.transport_graph.apply_electron_updates(electron_updates)
    result_object.lattice.transport_graph.dirty_nodes = list(
        result_object.lattice.transport_graph._graph.nodes
    )
    update.persist(result_object)
    _register_result_object(result_object)
    app_log.debug(f"Redispatch result object: {result_object}")

    return result_object.dispatch_id


def get_result_object(dispatch_id: str) -> Result:
    return _registered_dispatches.get(dispatch_id)


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
    if parent_eid := result_object._electron_id:
        dispatch_id, node_id = resolve_electron_id(parent_eid)
        status = result_object.status
        if status == RESULT_STATUS.POSTPROCESSING_FAILED:
            status = RESULT_STATUS.FAILED
        parent_result_obj = get_result_object(dispatch_id)
        node_result = generate_node_result(
            dispatch_id=dispatch_id,
            node_id=node_id,
            node_name=parent_result_obj.lattice.transport_graph.get_node_value(node_id, "name"),
            end_time=result_object.end_time,
            status=status,
            output=result_object._result,
            error=result_object._error,
            sub_dispatch_id=load.sublattice_dispatch_id(parent_eid),
            sublattice_result=result_object,
        )

        app_log.debug(f"Updating sublattice parent node {dispatch_id}:{node_id}")
        await update_node_result(parent_result_obj, node_result)


def upsert_lattice_data(dispatch_id: str):
    result_object = get_result_object(dispatch_id)
    upsert.lattice_data(result_object)
