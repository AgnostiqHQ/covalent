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


from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .._serialize.common import deserialize_asset, load_asset
from .._serialize.electron import ASSET_FILENAME_MAP as ELECTRON_ASSET_FILENAMES
from .._serialize.electron import ASSET_TYPES as ELECTRON_ASSET_TYPES
from .._serialize.lattice import ASSET_FILENAME_MAP as LATTICE_ASSET_FILENAMES
from .._serialize.lattice import ASSET_TYPES as LATTICE_ASSET_TYPES
from .._serialize.result import ASSET_FILENAME_MAP as RESULT_ASSET_FILENAMES
from .._serialize.result import ASSET_TYPES as RESULT_ASSET_TYPES
from .._serialize.result import deserialize_result
from .._shared_files import logger
from .._shared_files.config import get_config
from .._shared_files.exceptions import MissingLatticeRecordError
from .._shared_files.schemas.asset import AssetSchema
from .._shared_files.schemas.result import ResultSchema
from .._shared_files.utils import copy_file_locally
from .result import Result, import_result_object
from .wait import EXTREME

app_log = logger.app_log
log_stack_info = logger.log_stack_info

multistage_get_result = get_config("sdk.multistage_dispatch") == "true"


SDK_NODE_META_KEYS = {
    "executor",
    "executor_data",
    "deps",
    "call_before",
    "call_after",
}

SDK_LAT_META_KEYS = {
    "executor",
    "executor_data",
    "workflow_executor",
    "workflow_executor_data",
    "deps",
    "call_before",
    "call_after",
}

DEFERRED_KEYS = {
    "output",
    "value",
    "result",
}


def _delete_result(
    dispatch_id: str,
    results_dir: str = None,
    remove_parent_directory: bool = False,
) -> None:
    """
    Internal function to delete the result.

    Args:
        dispatch_id: The dispatch id of the result.
        results_dir: The directory where the results are stored in dispatch id named folders.
        remove_parent_directory: Status of whether to delete the parent directory when removing the result.

    Returns:
        None

    Raises:
        FileNotFoundError: If the result file is not found.
    """

    if results_dir is None:
        results_dir = os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir")

    import shutil

    result_folder_path = os.path.join(results_dir, f"{dispatch_id}")

    if os.path.exists(result_folder_path):
        shutil.rmtree(result_folder_path, ignore_errors=True)

    with contextlib.suppress(OSError):
        os.rmdir(results_dir)

    if remove_parent_directory:
        shutil.rmtree(results_dir, ignore_errors=True)


def redispatch_result(result_object: Result, dispatcher: str = None) -> str:
    """
    Function to redispatch the result as a new dispatch.

    Args:
        result_object: The result object to be redispatched.
        dispatcher: The address to the dispatcher in the form of hostname:port, e.g. "localhost:8080".
    Returns:
        dispatch_id: The dispatch id of the new dispatch.
    """

    result_object._lattice.metadata["dispatcher"] = (
        dispatcher or result_object.lattice.metadata["dispatcher"]
    )

    return result_object.lattice._server_dispatch(result_object)


def sync(
    dispatch_id: Optional[Union[List[str], str]] = None,
) -> None:
    """
    Synchronization call. Returns when one or more dispatches have completed.

    Args:
        dispatch_id: One or more dispatch IDs to wait for before returning.

    Returns:
        None
    """

    # if isinstance(dispatch_id, str):
    #     _get_result_from_dispatcher(dispatch_id, wait=True, status_only=True)
    # elif isinstance(dispatch_id, list):
    #     for d in dispatch_id:
    #         _get_result_from_dispatcher(d, wait=True, status_only=True)
    # else:
    #     raise Exception(
    #         f"dispatch_id must be a string or a list. You passed a {type(dispatch_id)}."
    #     )

    pass


def cancel(dispatch_id: str, task_ids: List[int] = None, dispatcher_addr: str = None) -> str:
    """
    Cancel a running dispatch.

    Args:
        dispatch_id: The dispatch id of the dispatch to be cancelled.
        task_ids: Optional, list of task ids to cancel within the workflow
        dispatcher_addr: Dispatcher server address, if None then defaults to the address set in Covalent's config.

    Returns:
        Cancellation response
    """

    if dispatcher_addr is None:
        dispatcher_addr = (
            get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
        )

    if task_ids is None:
        task_ids = []

    url = f"http://{dispatcher_addr}/api/cancel"

    if isinstance(task_ids, int):
        task_ids = [task_ids]

    r = requests.post(url, json={"dispatch_id": dispatch_id, "task_ids": task_ids})
    r.raise_for_status()
    return r.content.decode("utf-8").strip().replace('"', "")


def _get_result_single(
    dispatch_id: str,
    wait: bool = False,
    dispatcher_addr: str = None,
    status_only: bool = False,
    *,
    workflow_output: bool = True,
    intermediate_outputs: bool = True,
    sublattice_results: bool = True,
) -> Result:
    """
    Get the results of a dispatch from a file.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Controls how long the method waits for the server to return a result. If False, the method will not wait and will return the current status of the workflow. If True, the method will wait for the result to finish and keep retrying for sys.maxsize.

    Returns:
        The result from the file.

    """

    try:
        result = _get_result_v2_from_dispatcher(
            dispatch_id=dispatch_id,
            wait=wait,
            status_only=status_only,
            dispatcher_addr=dispatcher_addr,
        )

        if status_only:
            return result

        result_export = result["result_export"]
        result_object = import_result_object(result_export)

        if workflow_output:
            _download_workflow_output(result_object, dispatcher_addr)

        if intermediate_outputs:
            _download_intermediate_outputs(result_object, dispatcher_addr)

        # Fetch sublattice result objects recursively
        tg = result_object.lattice.transport_graph
        for node_id in tg._graph.nodes:
            sub_dispatch_id = tg.get_node_value(node_id, "sub_dispatch_id")
            if sublattice_results and sub_dispatch_id:
                sub_result = get_result(
                    sub_dispatch_id,
                    wait,
                    dispatcher_addr,
                    status_only,
                    workflow_output=workflow_output,
                    intermediate_outputs=intermediate_outputs,
                    sublattice_results=sublattice_results,
                )
                tg.set_node_value(node_id, "sublattice_result", sub_result)
            else:
                tg.set_node_value(node_id, "sublattice_result", None)

    except MissingLatticeRecordError as ex:
        app_log.warning(
            f"Dispatch ID {dispatch_id} was not found in the database. Incorrect dispatch id."
        )

        raise ex

    return result_object


def _get_result_v2_from_dispatcher(
    dispatch_id: str,
    wait: bool = False,
    status_only: bool = False,
    dispatcher_addr: str = None,
) -> Dict:
    """
    Internal function to get the results of a dispatch from the server without checking if it is ready to read.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Controls how long the method waits for the server to return a result. If False, the method will not wait and will return the current status of the workflow. If True, the method will wait for the result to finish and keep retrying for sys.maxsize.
        status_only: If true, only returns result status, not the full result object, default is False.
        dispatcher_addr: Dispatcher server address, defaults to the address set in covalent.config.

    Returns:
        The result object from the server.

    Raises:
        MissingLatticeRecordError: If the result is not found.
    """

    if dispatcher_addr is None:
        dispatcher_addr = (
            get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
        )

    retries = int(EXTREME) if wait else 5

    adapter = HTTPAdapter(max_retries=Retry(total=retries, backoff_factor=1))
    http = requests.Session()
    http.mount("http://", adapter)
    url = "http://" + dispatcher_addr + "/api/v1/resultv2/" + dispatch_id
    response = http.get(
        url,
        params={"wait": bool(int(wait)), "status_only": status_only},
    )
    if response.status_code == 404:
        raise MissingLatticeRecordError
    response.raise_for_status()
    result = response.json()
    return result


def get_node_output(
    dispatch_id: str,
    node_id: int,
    dispatcher_addr: str = None,
) -> Dict:
    return _get_node_output_from_dispatcher(
        dispatch_id,
        node_id,
        dispatcher_addr,
    )


def get_workflow_output(
    dispatch_id: str,
    dispatcher_addr: str = None,
) -> Dict:
    return _get_dispatch_result_from_dispatcher(
        dispatch_id,
        dispatcher_addr,
    )


def _get_node_output_from_dispatcher(
    dispatch_id: str,
    node_id: int,
    dispatcher_addr: str = None,
) -> Dict:
    """
    Internal function to get the results of a dispatch from the server without checking if it is ready to read.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Controls how long the method waits for the server to return a result. If False, the method will not wait and will return the current status of the workflow. If True, the method will wait for the result to finish and keep retrying for sys.maxsize.
        status_only: If true, only returns result status, not the full result object, default is False.
        dispatcher: Dispatcher server address, defaults to the address set in covalent.config.

    Returns:
        The result object from the server.

    Raises:
        MissingLatticeRecordError: If the result is not found.
    """

    if dispatcher_addr is None:
        dispatcher_addr = (
            get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
        )

    url = f"http://{dispatcher_addr}/api/v1/assets/{dispatch_id}/node/{node_id}/output"

    response = requests.get(url, stream=True)

    if response.status_code == 404:
        raise MissingLatticeRecordError
    response.raise_for_status()

    return deserialize_asset(response.content, ELECTRON_ASSET_TYPES["output"])


def _download_intermediate_outputs(result_object: Result, dispatcher_addr: str):
    tg = result_object.lattice.transport_graph
    for node_id in tg._graph.nodes:
        output = _get_node_output_from_dispatcher(
            result_object.dispatch_id, node_id, dispatcher_addr
        )
        tg.set_node_value(node_id, "output", output)
    return result_object


def _get_dispatch_result_from_dispatcher(
    dispatch_id: str,
    dispatcher_addr: str = None,
) -> Dict:
    if dispatcher_addr is None:
        dispatcher_addr = (
            get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
        )

    url = f"http://{dispatcher_addr}/api/v1/assets/{dispatch_id}/dispatch/result"

    response = requests.get(url, stream=True)

    if response.status_code == 404:
        raise MissingLatticeRecordError
    response.raise_for_status()

    return deserialize_asset(response.content, RESULT_ASSET_TYPES["result"])


def _download_workflow_output(result_object: Result, dispatcher_addr: str):
    result_object._result = _get_dispatch_result_from_dispatcher(
        result_object.dispatch_id,
        dispatcher_addr,
    )
    return result_object


# Multi-part


def _get_result_export_from_dispatcher(
    dispatch_id: str,
    wait: bool = False,
    status_only: bool = False,
    dispatcher_addr: str = None,
) -> ResultSchema:
    """
    Internal function to get the results of a dispatch from the server without checking if it is ready to read.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Controls how long the method waits for the server to return a result. If False, the method will not wait and will return the current status of the workflow. If True, the method will wait for the result to finish and keep retrying for sys.maxsize.
        status_only: If true, only returns result status, not the full result object, default is False.
        dispatcher_addr: Dispatcher server address, defaults to the address set in covalent.config.

    Returns:
        The result object from the server.

    Raises:
        MissingLatticeRecordError: If the result is not found.
    """

    if dispatcher_addr is None:
        dispatcher_addr = (
            get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port"))
        )

    retries = int(EXTREME) if wait else 5

    adapter = HTTPAdapter(max_retries=Retry(total=retries, backoff_factor=1))
    http = requests.Session()
    http.mount("http://", adapter)
    url = "http://" + dispatcher_addr + "/api/v1/export/" + dispatch_id
    response = http.get(
        url,
        params={"wait": bool(int(wait)), "status_only": status_only},
    )
    if response.status_code == 404:
        raise MissingLatticeRecordError
    response.raise_for_status()
    export = response.json()
    return export


# Function to download default assets
def _get_default_assets(rm: ResultManager):
    for key in RESULT_ASSET_TYPES.keys():
        if key not in DEFERRED_KEYS:
            rm.download_result_asset(key)
            rm.load_result_asset(key)

    for key in LATTICE_ASSET_TYPES.keys():
        if key not in DEFERRED_KEYS:
            rm.download_lattice_asset(key)
            rm.load_lattice_asset(key)

    tg = rm.result_object.lattice.transport_graph

    tg.lattice_metadata = rm.result_object.lattice.metadata
    rm.result_object.lattice.__doc__ = rm.result_object.lattice.__dict__.pop("doc")

    for key in ELECTRON_ASSET_TYPES.keys():
        if key not in DEFERRED_KEYS:
            for node_id in tg._graph.nodes:
                rm.download_node_asset(node_id, key)
                rm.load_node_asset(node_id, key)


# Functions for computing local URIs
def get_node_asset_path(results_dir: str, node_id: int, key: str):
    filename = ELECTRON_ASSET_FILENAMES[key]
    return results_dir + f"/node_{node_id}/{filename}"


def get_lattice_asset_path(results_dir: str, key: str):
    filename = LATTICE_ASSET_FILENAMES[key]
    return results_dir + f"/{filename}"


def get_result_asset_path(results_dir: str, key: str):
    filename = RESULT_ASSET_FILENAMES[key]
    return results_dir + f"/{filename}"


# Asset transfers


def download_asset(remote_uri: str, local_path: str, chunk_size: int = 1024 * 1024):
    local_scheme = "file"
    if remote_uri.startswith(local_scheme):
        copy_file_locally(remote_uri, f"file://{local_path}")
    else:
        r = requests.get(remote_uri, stream=True)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)


def _download_result_asset(manifest: dict, results_dir: str, key: str):
    remote_uri = manifest["assets"][key]["remote_uri"]
    local_path = get_result_asset_path(results_dir, key)
    download_asset(remote_uri, local_path)
    manifest["assets"][key]["uri"] = "file://" + local_path


def _download_lattice_asset(manifest: dict, results_dir: str, key: str):
    lattice_assets = manifest["lattice"]["assets"]
    remote_uri = lattice_assets[key]["remote_uri"]
    local_path = get_lattice_asset_path(results_dir, key)
    download_asset(remote_uri, local_path)
    lattice_assets[key]["uri"] = "file://" + local_path


def _download_node_asset(manifest: dict, results_dir: str, node_id: int, key: str):
    node = manifest["lattice"]["transport_graph"]["nodes"][node_id]
    node_assets = node["assets"]
    remote_uri = node_assets[key]["remote_uri"]
    local_path = get_node_asset_path(results_dir, node_id, key)
    download_asset(remote_uri, local_path)
    node_assets[key]["uri"] = "file://" + local_path


def _load_result_asset(manifest: dict, key: str):
    asset_meta = AssetSchema(**manifest["assets"][key])
    return load_asset(asset_meta, RESULT_ASSET_TYPES[key])


def _load_lattice_asset(manifest: dict, key: str):
    asset_meta = AssetSchema(**manifest["lattice"]["assets"][key])
    return load_asset(asset_meta, LATTICE_ASSET_TYPES[key])


def _load_node_asset(manifest: dict, node_id: int, key: str):
    node = manifest["lattice"]["transport_graph"]["nodes"][node_id]
    asset_meta = AssetSchema(**node["assets"][key])
    return load_asset(asset_meta, ELECTRON_ASSET_TYPES[key])


class ResultManager:
    def __init__(self, manifest: ResultSchema, results_dir: str):
        self.result_object = deserialize_result(manifest)
        self._manifest = manifest.dict()
        self._results_dir = results_dir

    def save(self, path: Optional[str] = None):
        if not path:
            path = os.path.join(self._results_dir, "manifest.json")
        with open(path, "w") as f:
            f.write(ResultSchema.parse_obj(self._manifest).json())

    @staticmethod
    def load(path: str, results_dir: str) -> "ResultManager":
        with open(path, "r") as f:
            manifest_json = f.read()

        return ResultManager(ResultSchema.parse_raw(manifest_json), results_dir)

    def download_result_asset(self, key: str):
        _download_result_asset(self._manifest, self._results_dir, key)

    def download_lattice_asset(self, key: str):
        _download_lattice_asset(self._manifest, self._results_dir, key)

    def download_node_asset(self, node_id: int, key: str):
        _download_node_asset(self._manifest, self._results_dir, node_id, key)

    def load_result_asset(self, key: str):
        data = _load_result_asset(self._manifest, key)
        self.result_object.__dict__[f"_{key}"] = data

    def load_lattice_asset(self, key: str):
        data = _load_lattice_asset(self._manifest, key)
        if key in SDK_LAT_META_KEYS:
            self.result_object.lattice.metadata[key] = data
        else:
            self.result_object.lattice.__dict__[key] = data

    def load_node_asset(self, node_id: int, key: str):
        data = _load_node_asset(self._manifest, node_id, key)
        tg = self.result_object.lattice.transport_graph
        if key in SDK_NODE_META_KEYS:
            node_meta = tg.get_node_value(node_id, "metadata")
            node_meta[key] = data
        else:
            tg.set_node_value(node_id, key, data)

    @staticmethod
    def from_dispatch_id(
        dispatch_id: str,
        results_dir: str,
        wait: bool = False,
        dispatcher_addr: str = None,
    ) -> "ResultManager":
        export = _get_result_export_from_dispatcher(
            dispatch_id, wait, status_only=False, dispatcher_addr=dispatcher_addr
        )

        manifest = ResultSchema.parse_obj(export["result_export"])

        # sort the nodes
        manifest.lattice.transport_graph.nodes.sort(key=lambda x: x.id)

        rm = ResultManager(manifest, results_dir)
        result_object = rm.result_object
        result_object._results_dir = results_dir
        Path(results_dir).mkdir(parents=True, exist_ok=True)

        # Create node subdirectories
        for node_id in result_object.lattice.transport_graph._graph.nodes:
            node_dir = results_dir + f"/node_{node_id}"
            Path(node_dir).mkdir(exist_ok=True)

        return rm


def get_result_manager(dispatch_id, results_dir=None, wait=False, dispatcher_addr=None):
    if not results_dir:
        results_dir = get_config("sdk.results_dir") + f"/{dispatch_id}"
    return ResultManager.from_dispatch_id(dispatch_id, results_dir, wait, dispatcher_addr)


def _get_result_multistage(
    dispatch_id: str,
    wait: bool = False,
    dispatcher_addr: str = None,
    status_only: bool = False,
    *,
    workflow_output: bool = True,
    intermediate_outputs: bool = True,
    sublattice_results: bool = True,
) -> Result:
    """
    Get the results of a dispatch from a file.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Controls how long the method waits for the server to return a result. If False, the method will not wait and will return the current status of the workflow. If True, the method will wait for the result to finish and keep retrying for sys.maxsize.

    Returns:
        The result from the file.

    """

    try:
        if status_only:
            return _get_result_export_from_dispatcher(
                dispatch_id=dispatch_id,
                wait=wait,
                status_only=status_only,
                dispatcher_addr=dispatcher_addr,
            )
        else:
            rm = get_result_manager(dispatch_id, None, wait, dispatcher_addr)
            _get_default_assets(rm)

        if workflow_output:
            rm.download_result_asset("result")
            rm.load_result_asset("result")

        if intermediate_outputs:
            tg = rm.result_object.lattice.transport_graph
            for node_id in tg._graph.nodes:
                rm.download_node_asset(node_id, "output")
                rm.load_node_asset(node_id, "output")

        # Fetch sublattice result objects recursively
        tg = rm.result_object.lattice.transport_graph
        for node_id in tg._graph.nodes:
            sub_dispatch_id = tg.get_node_value(node_id, "sub_dispatch_id")
            if sublattice_results and sub_dispatch_id:
                sub_result = _get_result_multistage(
                    sub_dispatch_id,
                    wait,
                    dispatcher_addr,
                    status_only,
                    workflow_output=workflow_output,
                    intermediate_outputs=intermediate_outputs,
                    sublattice_results=sublattice_results,
                )
                tg.set_node_value(node_id, "sublattice_result", sub_result)
            else:
                tg.set_node_value(node_id, "sublattice_result", None)

    except MissingLatticeRecordError as ex:
        app_log.warning(
            f"Dispatch ID {dispatch_id} was not found in the database. Incorrect dispatch id."
        )

        raise ex

    return rm.result_object


def get_result(
    dispatch_id: str,
    wait: bool = False,
    dispatcher_addr: str = None,
    status_only: bool = False,
    *,
    workflow_output: bool = True,
    intermediate_outputs: bool = True,
    sublattice_results: bool = True,
    multistage: bool = multistage_get_result,
) -> Result:
    if multistage:
        return _get_result_multistage(
            dispatch_id=dispatch_id,
            wait=wait,
            dispatcher_addr=dispatcher_addr,
            status_only=status_only,
            workflow_output=workflow_output,
            intermediate_outputs=intermediate_outputs,
            sublattice_results=sublattice_results,
        )
    else:
        return _get_result_single(
            dispatch_id=dispatch_id,
            wait=wait,
            dispatcher_addr=dispatcher_addr,
            status_only=status_only,
            workflow_output=workflow_output,
            intermediate_outputs=intermediate_outputs,
            sublattice_results=sublattice_results,
        )
