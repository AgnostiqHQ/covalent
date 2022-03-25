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


import os
import pickle as _pickle
from pathlib import Path
from typing import List, Optional, Union

import cloudpickle as pickle

from .._shared_files import logger
from .._shared_files.config import get_config
from .result import Result

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def get_result(
    dispatch_id: str, results_dir: str = get_config("dispatcher.results_dir"), wait: bool = False
) -> Result:
    """
    Get the results of a dispatch from a file.

    Args:
        dispatch_id: The dispatch id of the result.
        results_dir: The directory where the results are stored in dispatch id named folders.
        wait: Whether to wait for the result to be completed/failed, default is False.

    Returns:
        result_object: The result from the file.

    Raises:
        RuntimeError: If the result is not ready to read yet.
        FileNotFoundError: If the result file is not found.
    """

    try:
        result_object = _get_result_from_file(dispatch_id, results_dir, wait)

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Result was not found in the specified directory. Please make sure it hasn't been moved or try a different directory than {results_dir}."
        )

    return result_object


def _get_result_from_file(
    dispatch_id: str, results_dir: str = get_config("dispatcher.results_dir"), wait: bool = False
) -> Result:

    """
    Internal function to get the results of a dispatch from a file without checking if it is ready to read.

    Args:
        dispatch_id: The dispatch id of the result.
        results_dir: The directory where the results are stored in dispatch id named folders.
        wait: Whether to wait for the result to be completed/failed, default is False.

    Returns:
        result_object: The result from the file.

    Raises:
        RuntimeError: If the result is found but is not ready to read yet.
        FileNotFoundError: If the result is not found.
    """

    results_dir_expanded = str(Path(results_dir).expanduser().resolve())
    result_dir = os.path.join(results_dir_expanded, f"{dispatch_id}")

    while True:
        try:
            with open(os.path.join(result_dir, "result.pkl"), "rb") as f:
                result = pickle.loads(f.read())

            if not wait:
                return result
            elif result.status in [Result.COMPLETED, Result.FAILED, Result.CANCELLED]:
                return result
        except (FileNotFoundError, EOFError, _pickle.UnpicklingError):
            if wait:
                continue
            raise RuntimeError(
                "Result not ready to read yet. Please wait for a couple of seconds."
            )


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
    dispatch_id: Optional[Union[List[str], str]] = None,
    results_dir: Optional[str] = get_config("dispatcher.results_dir"),
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
        _get_result_from_file(dispatch_id, results_dir, True)
    elif isinstance(dispatch_id, list):
        for d in dispatch_id:
            _get_result_from_file(d, results_dir, True)
    else:
        from glob import glob

        dirs = glob(f"{results_dir}/*/")
        for d in dirs:
            dispatch_id = os.path.basename(d.rstrip("/"))
            _get_result_from_file(dispatch_id, results_dir, True)


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

    import requests

    url = "http://" + dispatcher + "/api/cancel"

    r = requests.post(url, data=dispatch_id.encode("utf-8"))
    r.raise_for_status()
    return r.content.decode("utf-8").strip().replace('"', "")
