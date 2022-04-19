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

from copy import deepcopy
from functools import wraps
from io import BytesIO
from typing import Callable, List, Union

import cloudpickle as pickle
import requests

from .._results_manager.result import Result
from .._workflow.lattice import Lattice
from . import get_svc_uri


def dispatch(
    orig_lattice: Lattice,
    queuer_addr: str = get_svc_uri.QueuerURI().get_route("submit/dispatch"),
) -> Callable:
    """
    Wrapping the dispatching functionality to allow input passing
    and server address specification.

    Afterwards, send the lattice to the dispatcher server and return
    the assigned dispatch id.

    Args:
        orig_lattice: The lattice/workflow to send to the dispatcher server.
        dispatcher_addr: The address of the dispatcher server.

    Returns:
        Wrapper function which takes the inputs of the workflow as arguments
    """

    @wraps(orig_lattice)
    def wrapper(*args, **kwargs) -> str:
        """
        Send the lattice to the dispatcher server and return
        the assigned dispatch id.

        Args:
            *args: The inputs of the workflow.
            **kwargs: The keyword arguments of the workflow.

        Returns:
            The dispatch id of the workflow.
        """

        lattice = deepcopy(orig_lattice)

        lattice.build_graph(*args, **kwargs)

        pickled_res = pickle.dumps(Result(lattice, lattice.metadata["results_dir"]))

        r = requests.post(queuer_addr, files={"result_pkl_file": BytesIO(pickled_res)})
        r.raise_for_status()

        # Returns assigned dispatch id
        return r.json()["dispatch_id"]

    return wrapper


def dispatch_sync(
    lattice: Lattice,
    queuer_addr: str = get_svc_uri.QueuerURI().get_route("submit/dispatch"),
) -> Callable:
    """
    Wrapping the synchronous dispatching functionality to allow input
    passing and server address specification.

    Afterwards, sends the lattice to the dispatcher server and return
    the result of the executed workflow.

    Args:
        orig_lattice: The lattice/workflow to send to the dispatcher server.
        dispatcher_addr: The address of the dispatcher server.

    Returns:
        Wrapper function which takes the inputs of the workflow as arguments
    """

    @wraps(lattice)
    def wrapper(*args, **kwargs) -> Result:
        """
        Send the lattice to the dispatcher server and return
        the result of the executed workflow.

        Args:
            *args: The inputs of the workflow.
            **kwargs: The keyword arguments of the workflow.

        Returns:
            The result of the executed workflow.
        """

        return get_result(
            dispatch_id=dispatch(lattice, queuer_addr)(*args, **kwargs),
            wait=True,
        )

    return wrapper


def _retrieve_result_response(session: requests.Session, dispatch_id: str) -> requests.Response:

    response = session.get(
        get_svc_uri.ResultsURI().get_route(f"workflow/results/{dispatch_id}"), stream=True
    )

    response.raise_for_status()

    return response


def _poll_result(
    session: requests.Session, dispatch_id: str, wait: bool = False
) -> requests.Response:

    response = _retrieve_result_response(session, dispatch_id)

    if wait:
        result_object: Result = pickle.loads(response.content)

        while result_object.status not in [Result.COMPLETED, Result.FAILED, Result.CANCELLED]:
            response = _retrieve_result_response(session, dispatch_id)
            result_object: Result = pickle.loads(response.content)

    return response


def get_result(dispatch_id: str, download=False, wait=False):

    session = requests.Session()

    response = _poll_result(session, dispatch_id, wait)

    if not download:
        return pickle.loads(response.content)

    filename = f"result_{dispatch_id}.pkl"
    with open(filename, "wb") as f:
        f.write(response.content)

    return filename


def cancel_workflow(dispatch_id: str):
    response = requests.delete(get_svc_uri.DispatcherURI().get_route(f"workflow/{dispatch_id}"))

    response.raise_for_status()

    return response.json()


def sync(dispatch_id: Union[List[str], str]) -> None:

    session = requests.Session()

    workflow_list = dispatch_id if isinstance(dispatch_id, list) else [dispatch_id]

    for workflow in workflow_list:
        _poll_result(session, workflow, True)
