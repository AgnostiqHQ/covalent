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

import traceback
import uuid
from typing import Any, Dict, List

from pydantic import ValidationError

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.schemas.result import ResultSchema
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice

from .._dal.result import Result as SRVResult
from .._dal.result import get_result_object as get_result_object_from_db
from .._db import update
from .._db.write_result_to_db import resolve_electron_id
from . import dispatcher
from .data_modules import graph
from .data_modules import importer as manifest_importer
from .data_modules.utils import run_in_executor

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def generate_node_result(
    node_id,
    node_name=None,
    start_time=None,
    end_time=None,
    status=None,
    output=None,
    error=None,
    stdout=None,
    stderr=None,
):
    return {
        "node_id": node_id,
        "node_name": node_name,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "output": output,
        "error": error,
        "stdout": stdout,
        "stderr": stderr,
    }


# Domain: result
async def update_node_result(dispatch_id, node_result):
    app_log.debug("Updating node result (run_planned_workflow).")
    valid_update = True
    try:
        node_id = node_result["node_id"]
        node_status = node_result["status"]
        node_info = await get_electron_attributes(
            dispatch_id, node_id, ["type", "sub_dispatch_id"]
        )
        node_type = node_info["type"]
        sub_dispatch_id = node_info["sub_dispatch_id"]

        # Handle returns from _build_sublattice_graph -- change
        # COMPLETED -> DISPATCHING
        node_result = await _filter_sublattice_status(
            dispatch_id, node_id, node_status, node_type, sub_dispatch_id, node_result
        )

        valid_update = await run_in_executor(_update_node, dispatch_id, node_result)
        if not valid_update:
            app_log.warning(
                f"Invalid status update {node_status} for node {dispatch_id}:{node_id}"
            )
            return

        if node_result["status"] == RESULT_STATUS.DISPATCHING:
            app_log.debug("Received sublattice dispatch")
            try:
                sub_dispatch_id = await _make_sublattice_dispatch(dispatch_id, node_result)
            except Exception as ex:
                tb = "".join(traceback.TracebackException.from_exception(ex).format())
                node_result["status"] = RESULT_STATUS.FAILED
                node_result["error"] = tb
                await run_in_executor(_update_node, dispatch_id, node_result)

    except KeyError as ex:
        valid_update = False
        app_log.exception(f"Error persisting node update: {ex}")

    except Exception as ex:
        app_log.exception(f"Error persisting node update: {ex}")
        sub_dispatch_id = None
        node_result["status"] = Result.FAILED

    finally:
        if not valid_update:
            return

        node_id = node_result["node_id"]
        node_status = node_result["status"]
        dispatch_id = dispatch_id

        detail = {"sub_dispatch_id": sub_dispatch_id} if sub_dispatch_id else {}
        if node_status and valid_update:
            await dispatcher.notify_node_status(dispatch_id, node_id, node_status, detail)


# To be run in a threadpool; move this to a static method of Result
def _update_node(dispatch_id: str, node_result: Dict):
    result_object = get_result_object(dispatch_id, bare=True)
    return result_object._update_node(**node_result)


# Domain: result
def initialize_result_object(
    json_lattice: str, parent_dispatch_id: str = None, parent_electron_id: int = None
) -> Result:
    """Convenience function for constructing a result object from a json-serialized lattice.

    Args:
        json_lattice: a JSON-serialized lattice
        parent_dispatch_id: the parent dispatch id if json_lattice is a sublattice
        parent_electron_id: the DB id of the parent electron (for sublattices)

    Returns:
        Result: result object
    """

    dispatch_id = get_unique_id()
    lattice = Lattice.deserialize_from_json(json_lattice)
    result_object = Result(lattice, dispatch_id)
    if parent_dispatch_id:
        parent_result_object = get_result_object(parent_dispatch_id, bare=True)
        result_object._root_dispatch_id = parent_result_object.root_dispatch_id

    result_object._electron_id = parent_electron_id
    result_object._initialize_nodes()
    app_log.debug("2: Constructed result object and initialized nodes.")

    update.persist(result_object, electron_id=parent_electron_id)
    app_log.debug("Result object persisted.")

    return result_object.dispatch_id


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
    json_lattice: str, parent_dispatch_id: str = None, parent_electron_id: int = None
) -> Result:
    return await run_in_executor(
        initialize_result_object,
        json_lattice,
        parent_dispatch_id,
        parent_electron_id,
    )


def get_result_object(dispatch_id: str, bare: bool = True) -> SRVResult:
    app_log.debug(f"Getting result object from db, bare={bare}")
    return get_result_object_from_db(dispatch_id, bare)


def finalize_dispatch(dispatch_id: str):
    app_log.debug(f"Finalizing dispatch {dispatch_id}")


async def persist_result(dispatch_id: str):
    await _update_parent_electron(dispatch_id)


async def _update_parent_electron(dispatch_id: str):
    dispatch_attrs = await get_dispatch_attributes(
        dispatch_id, ["electron_id", "status", "end_time"]
    )
    parent_eid = dispatch_attrs["electron_id"]

    if parent_eid:
        dispatch_id, node_id = resolve_electron_id(parent_eid)
        status = dispatch_attrs["status"]
        if status == Result.POSTPROCESSING_FAILED:
            status = Result.FAILED
        node_result = generate_node_result(
            node_id=node_id,
            end_time=dispatch_attrs["end_time"],
            status=status,
        )
        parent_result_obj = get_result_object(dispatch_id)
        app_log.debug(f"Updating sublattice parent node {dispatch_id}:{node_id}")
        await update_node_result(parent_result_obj.dispatch_id, node_result)


def _get_attrs_for_electrons_sync(
    dispatch_id: str, node_ids: List[int], keys: List[str]
) -> List[Dict]:
    result_object = get_result_object(dispatch_id)
    attrs = result_object.lattice.transport_graph.get_values_for_nodes(
        node_ids=node_ids,
        keys=keys,
        refresh=False,
    )
    return attrs


async def get_attrs_for_electrons(
    dispatch_id: str, node_ids: List[int], keys: List[str]
) -> List[Dict]:
    """Query attributes for multiple electrons.

    Args:
        node_ids: The list of nodes to query
        keys: The list of attributes to query for each electron

    Returns:
        A list of dictionaries {attr_key: attr_val}, one for
        each node id, in the same order as `node_ids`

    Example:
    ```
        await get_attrs_for_electrons(
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
        _get_attrs_for_electrons_sync,
        dispatch_id,
        node_ids,
        keys,
    )


async def get_electron_attributes(dispatch_id: str, node_id: int, keys: List[str]) -> Dict:
    """Convenience function to query attributes for an electron.

    Args:
        node_id: The node to query
        keys: The list of attributes to query

    Returns:
        A dictionary {attr_key: attr_val}

    Example:
    ```
        await get_electron_attributes(
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
    attrs = await get_attrs_for_electrons(dispatch_id, [node_id], keys)
    return attrs[0]


async def _filter_sublattice_status(
    dispatch_id, node_id, status, node_type, sub_dispatch_id, node_result
):
    if status == Result.COMPLETED and node_type == "sublattice" and not sub_dispatch_id:
        node_result["status"] = RESULT_STATUS.DISPATCHING
    return node_result


async def _make_sublattice_dispatch(dispatch_id: str, node_result: dict):
    try:
        manifest, parent_electron_id = await run_in_executor(
            _make_sublattice_dispatch_helper,
            dispatch_id,
            node_result,
        )

        imported_manifest = await manifest_importer.import_manifest(
            manifest=manifest,
            parent_dispatch_id=dispatch_id,
            parent_electron_id=parent_electron_id,
        )

        return imported_manifest.metadata.dispatch_id

    except ValidationError as ex:
        # Fall back to legacy sublattice handling
        # NB: this loads the JSON sublattice in memory
        json_lattice, parent_electron_id = await run_in_executor(
            _legacy_sublattice_dispatch_helper,
            dispatch_id,
            node_result,
        )
        return await make_dispatch(
            json_lattice,
            dispatch_id,
            parent_electron_id,
        )


def _legacy_sublattice_dispatch_helper(dispatch_id: str, node_result: Dict):
    app_log.debug("falling back to legacy sublattice dispatch")

    result_object = get_result_object(dispatch_id, bare=True)
    node_id = node_result["node_id"]
    parent_node = result_object.lattice.transport_graph.get_node(node_id)
    bg_output = parent_node.get_value("output")

    parent_electron_id = parent_node._electron_id
    json_lattice = bg_output.object_string
    return json_lattice, parent_electron_id


def _make_sublattice_dispatch_helper(dispatch_id: str, node_result: Dict):
    """Helper function for performing DB queries"""
    result_object = get_result_object(dispatch_id, bare=True)
    node_id = node_result["node_id"]
    parent_node = result_object.lattice.transport_graph.get_node(node_id)
    bg_output = parent_node.get_value("output")

    manifest = ResultSchema.parse_raw(bg_output.object_string)
    parent_electron_id = parent_node._electron_id

    return manifest, parent_electron_id


# Common Result object queries

# Dispatch


def generate_dispatch_result(
    dispatch_id,
    start_time=None,
    end_time=None,
    status=None,
    error=None,
    result=None,
):
    return {
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "error": error,
        "result": result,
    }


def _update_dispatch_result_sync(dispatch_id, dispatch_result):
    result_object = get_result_object(dispatch_id)
    result_object._update_dispatch(**dispatch_result)


async def update_dispatch_result(dispatch_id, dispatch_result):
    await run_in_executor(_update_dispatch_result_sync, dispatch_id, dispatch_result)


def _get_dispatch_attributes_sync(dispatch_id: str, keys: List[str]) -> Any:
    refresh = False
    result_object = get_result_object(dispatch_id)
    return result_object.get_values(keys, refresh=refresh)


def _get_lattice_attributes_sync(dispatch_id: str, keys: List[str]) -> Any:
    refresh = False
    result_object = get_result_object(dispatch_id)
    return result_object.lattice.get_values(keys, refresh=refresh)


async def get_dispatch_attributes(dispatch_id: str, keys: List[str]) -> Dict:
    return await run_in_executor(
        _get_dispatch_attributes_sync,
        dispatch_id,
        keys,
    )


async def get_lattice_attributes(dispatch_id: str, keys: List[str]) -> Dict:
    return await run_in_executor(
        _get_lattice_attributes_sync,
        dispatch_id,
        keys,
    )


# Ensure that a dispatch is only run once; in the future, also check
# if all assets have been uploaded
def _ensure_dispatch_sync(dispatch_id: str) -> bool:
    return SRVResult.ensure_run_once(dispatch_id)


async def ensure_dispatch(dispatch_id: str) -> bool:
    """Check if a dispatch can be run.

    The following criteria must be met:
    * The dispatch has not been run before.
    * (later) all assets have been uploaded
    """
    return await run_in_executor(
        _ensure_dispatch_sync,
        dispatch_id,
    )


# Graph queries


async def get_incomplete_tasks(dispatch_id: str):
    # Need to filter all electrons in the latice
    return await run_in_executor(_get_incomplete_tasks_sync, dispatch_id)


def _get_incomplete_tasks_sync(dispatch_id: str):
    result_object = get_result_object(dispatch_id, False)
    refresh = False
    return result_object._get_incomplete_nodes(refresh)


async def get_incoming_edges(dispatch_id: str, node_id: int):
    return await run_in_executor(graph.get_incoming_edges, dispatch_id, node_id)


async def get_node_successors(
    dispatch_id: str,
    node_id: int,
    attrs: List[str] = ["task_group_id"],
) -> List[Dict]:
    return await run_in_executor(graph.get_node_successors, dispatch_id, node_id, attrs)


async def get_graph_nodes_links(dispatch_id: str) -> dict:
    return await run_in_executor(graph.get_graph_nodes_links, dispatch_id)


async def get_nodes(dispatch_id: str) -> List[int]:
    return await run_in_executor(graph.get_nodes, dispatch_id)
