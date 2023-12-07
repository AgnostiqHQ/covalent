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
import tempfile
import traceback
from typing import Dict

from pydantic import ValidationError

from covalent._dispatcher_plugins.local import LocalDispatcher
from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.schemas.result import ResultSchema
from covalent._shared_files.util_classes import RESULT_STATUS
from covalent._workflow.lattice import Lattice

from .._dal.result import Result as SRVResult
from .._dal.result import get_result_object as get_result_object_from_db
from .._db.write_result_to_db import resolve_electron_id
from . import dispatcher
from .data_modules import dispatch, electron  # nopycln: import
from .data_modules import importer as manifest_importer
from .data_modules.utils import run_in_executor

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def generate_node_result(
    node_id: int,
    node_name: str = None,
    start_time=None,
    end_time=None,
    status=None,
    output=None,
    error=None,
    stdout=None,
    stderr=None,
    qelectron_data_exists=None,
):
    """
    Helper routine to prepare the node result

    Arg(s)
        node_id: ID of the node in the trasport graph
        node_name: Name of the node
        start_time: Start time of the node
        end_time: Time at which the node finished executing
        status: Status of the node's execution
        output: Output of the node
        error: Error from the node
        stdout: STDOUT of a node
        stderr: STDERR generated during node execution
        qelectron_data_exists: Whether the qelectron data exists

    Return(s)
        Dictionary of the inputs
    """

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
        "qelectron_data_exists": qelectron_data_exists,  # TODO: This field is now defunct, see PR #1850
    }


# Domain: result
async def update_node_result(dispatch_id, node_result):
    app_log.debug("Updating node result (run_planned_workflow).")
    valid_update = True
    try:
        node_id = node_result["node_id"]
        node_status = node_result["status"]
        node_info = await electron.get(dispatch_id, node_id, ["type", "sub_dispatch_id"])
        node_type = node_info["type"]
        sub_dispatch_id = node_info["sub_dispatch_id"]

        # Handle returns from _build_sublattice_graph -- change
        # COMPLETED -> DISPATCHING
        node_result = _filter_sublattice_status(
            dispatch_id, node_id, node_status, node_type, sub_dispatch_id, node_result
        )

        valid_update = await electron.update(dispatch_id, node_result)
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
                await electron.update(dispatch_id, node_result)

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
        detail = {"sub_dispatch_id": sub_dispatch_id} if sub_dispatch_id else {}

        if node_status and valid_update:
            dispatch_id = dispatch_id
            await dispatcher.notify_node_status(dispatch_id, node_id, node_status, detail)


# Domain: result
def _redirect_lattice(
    json_lattice: str,
    parent_dispatch_id: str,
    parent_electron_id: int,
    loop: asyncio.AbstractEventLoop,
) -> str:
    """Redirect a JSON lattice through the new DAL.

    Args:
        json_lattice: A JSON-serialized lattice.
        parent_dispatch_id:  The id of a sublattice's parent dispatch.

    This will only be triggered from either the monolithic /submit
    endpoint or a monolithic sublattice dispatch.

    Returns:
        The dispatch manifest

    """
    lattice = Lattice.deserialize_from_json(json_lattice)
    with tempfile.TemporaryDirectory() as staging_dir:
        manifest = LocalDispatcher.prepare_manifest(lattice, staging_dir)

        # Trigger an internal asset pull from /tmp to object store
        coro = manifest_importer.import_manifest(
            manifest,
            parent_dispatch_id,
            parent_electron_id,
        )
        filtered_manifest = manifest_importer._import_manifest(
            manifest,
            parent_dispatch_id,
            parent_electron_id,
        )

        manifest_importer._pull_assets(filtered_manifest)

    return filtered_manifest.metadata.dispatch_id


async def make_dispatch(
    json_lattice: str, parent_dispatch_id: str = None, parent_electron_id: int = None
) -> str:
    return await run_in_executor(
        _redirect_lattice,
        json_lattice,
        parent_dispatch_id,
        parent_electron_id,
        asyncio.get_running_loop(),
    )


def get_result_object(dispatch_id: str, bare: bool = True) -> SRVResult:
    app_log.debug(f"Getting result object from db, bare={bare}")
    return get_result_object_from_db(dispatch_id, bare)


def finalize_dispatch(dispatch_id: str):
    app_log.debug(f"Finalizing dispatch {dispatch_id}")


async def persist_result(dispatch_id: str):
    await _update_parent_electron(dispatch_id)


async def _update_parent_electron(dispatch_id: str):
    dispatch_attrs = await dispatch.get(dispatch_id, ["electron_id", "status", "end_time"])
    parent_eid = dispatch_attrs["electron_id"]

    if parent_eid:
        dispatch_id, node_id = resolve_electron_id(parent_eid)
        status = dispatch_attrs["status"]
        node_result = generate_node_result(
            node_id=node_id,
            end_time=dispatch_attrs["end_time"],
            status=status,
        )
        parent_result_obj = get_result_object(dispatch_id)
        app_log.debug(f"Updating sublattice parent node {dispatch_id}:{node_id}")
        await update_node_result(parent_result_obj.dispatch_id, node_result)


def _filter_sublattice_status(
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
    """Helper function for performing DB queries related to sublattices."""
    result_object = get_result_object(dispatch_id, bare=True)
    node_id = node_result["node_id"]
    parent_node = result_object.lattice.transport_graph.get_node(node_id)
    bg_output = parent_node.get_value("output")

    manifest = ResultSchema.parse_raw(bg_output.object_string)
    parent_electron_id = parent_node._electron_id

    return manifest, parent_electron_id


# Common Result object queries


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


# Ensure that a dispatch is only run once; in the future, also check
# if all assets have been uploaded


async def ensure_dispatch(dispatch_id: str) -> bool:
    """Check if a dispatch can be run.

    The following criteria must be met:
    * The dispatch has not been run before.
    * (later) all assets have been uploaded
    """
    return await run_in_executor(
        SRVResult.ensure_run_once,
        dispatch_id,
    )
