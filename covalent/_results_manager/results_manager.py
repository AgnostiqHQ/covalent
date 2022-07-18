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


import codecs
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

import cloudpickle as pickle
import requests
from requests.adapters import HTTPAdapter
from sqlalchemy.orm import Session

from covalent._workflow.transport import TransportableObject

from .. import _workflow as ct
from .._data_store.datastore import DataStore
from .._data_store.models import Lattice
from .._shared_files import logger
from .._shared_files.config import get_config
from .result import Result
from .utils import _db_path
from .write_result_to_db import MissingLatticeRecordError

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def get_data_store() -> DataStore:
    return DataStore(db_URL=f"sqlite+pysqlite:///{_db_path()}")


def get_result(dispatch_id: str, wait: bool = False) -> Result:
    """
    Get the results of a dispatch from a file.

    Args:
        dispatch_id: The dispatch id of the result.
        results_dir: The directory where the results are stored in dispatch id named folders.
        wait: Whether to wait for the result to be completed/failed, default is False.

    Returns:
        result_object: The result from the file.

    """

    try:
        result = _get_result_from_dispatcher(
            dispatch_id,
            wait,
        )
        result_object = pickle.loads(codecs.decode(result["result"].encode(), "base64"))

    except MissingLatticeRecordError as e:
        app_log.warning(
            f"Dispatch ID {dispatch_id} was not found in the database. Either the Dispatch ID is incorrect or wait a couple of seconds before trying again."
        )

        time.sleep(0.01)
        return get_result(dispatch_id, wait)

    return result_object


def result_from(lattice_record: Lattice) -> Result:
    with open(
        os.path.join(lattice_record.storage_path, lattice_record.function_filename), "rb"
    ) as f:
        function = pickle.loads(f.read())
    with open(
        os.path.join(lattice_record.storage_path, lattice_record.executor_filename), "rb"
    ) as f:
        executor = pickle.loads(f.read())
    with open(
        os.path.join(lattice_record.storage_path, lattice_record.inputs_filename), "rb"
    ) as f:
        inputs = pickle.loads(f.read())
    with open(os.path.join(lattice_record.storage_path, lattice_record.error_filename), "rb") as f:
        error = pickle.loads(f.read())
    with open(
        os.path.join(lattice_record.storage_path, lattice_record.transport_graph_filename), "rb"
    ) as f:
        transport_graph = pickle.loads(f.read())
    with open(
        os.path.join(lattice_record.storage_path, lattice_record.results_filename), "rb"
    ) as f:
        output = pickle.loads(f.read())

    attributes = {
        "metadata": {"executor": executor},
        "args": inputs["args"],
        "kwargs": inputs["kwargs"],
        "transport_graph": transport_graph,
        "workflow_function": function,
    }

    def dummy_function(x):
        return x

    lat = ct.lattice(dummy_function)
    lat.__dict__ = attributes

    result = Result(
        lat,
        str(Path(lattice_record.storage_path).parent),
        dispatch_id=lattice_record.dispatch_id,
    )
    result._status = lattice_record.status
    result._error = error
    result._inputs = inputs
    result._start_time = lattice_record.started_at
    result._end_time = lattice_record.completed_at
    result._result = output if output is not None else TransportableObject(None)
    return result


def _get_result_from_dispatcher(
    dispatch_id: str,
    wait: bool = False,
    dispatcher: str = get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port")),
    status_only: bool = False,
) -> Dict:

    """
    Internal function to get the results of a dispatch from the server without checking if it is ready to read.

    Args:
        dispatch_id: The dispatch id of the result.
        wait: Whether to wait for the result to be completed/failed, default is False.
        status_only: If true, only returns result status, not the full result object, default is False.
        dispatcher: Dispatcher server address, defaults to the address set in covalent.config.

    Returns:
        The result object from the server.

    Raises:
        MissingLatticeRecordError: If the result is not found.
    """
    adapter = HTTPAdapter()
    http = requests.Session()
    http.mount("http://", adapter)
    url = "http://" + dispatcher + "/api/result/" + dispatch_id
    response = http.get(url, params={"wait": wait, "status_only": status_only})
    if response.status_code == 404:
        raise MissingLatticeRecordError
    response.raise_for_status()
    result = response.json()
    return result


def _delete_result(
    dispatch_id: str,
    results_dir: str = get_config("dispatcher.results_dir"),
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

    import shutil

    result_folder_path = os.path.join(results_dir, f"{dispatch_id}")

    if os.path.exists(result_folder_path):
        shutil.rmtree(result_folder_path, ignore_errors=True)

    try:
        os.rmdir(results_dir)
    except OSError:
        pass

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
    db: DataStore,
    dispatch_id: Optional[Union[List[str], str]] = None,
) -> None:
    """
    Synchronization call. Returns when one or more dispatches have completed.

    Args:
        dispatch_id: One or more dispatch IDs to wait for before returning.
        results_dir: The directory where results objects are stored.

    Returns:
        None
    """

    if isinstance(dispatch_id, str):
        _get_result_from_dispatcher(dispatch_id, wait=True, status_only=True)
    elif isinstance(dispatch_id, list):
        for d in dispatch_id:
            _get_result_from_dispatcher(d, wait=True, status_only=True)
    else:
        with Session(db.engine) as session:
            dispatch_id = session.query(Lattice.dispatch_id).all()
        for d in dispatch_id:
            _get_result_from_dispatcher(d, wait=True, status_only=True)


def cancel(
    dispatch_id: str,
    dispatcher: str = get_config("dispatcher.address") + ":" + str(get_config("dispatcher.port")),
) -> str:
    """
    Cancel a running dispatch.

    Args:
        dispatch_id: The dispatch id of the dispatch to be cancelled.
        dispatcher: The address to the dispatcher in the form of hostname:port, e.g. "localhost:8080".

    Returns:
        None
    """

    url = "http://" + dispatcher + "/api/cancel"

    r = requests.post(url, data=dispatch_id.encode("utf-8"))
    r.raise_for_status()
    return r.content.decode("utf-8").strip().replace('"', "")
