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


"""Functions to dispatch a workflow and get result of a workflow"""

# Include a download to file parameter to allow user to save the result in a file if required

from copy import deepcopy
from functools import wraps
from io import BytesIO

import cloudpickle as pickle
import get_svc_uri
import requests

from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice

SUBMIT_DISPATCH_QUEUER_ADDR = get_svc_uri.QueuerURI().get_route("submit/dispatch")


def dispatch(
    orig_lattice: Lattice,
):
    @wraps(orig_lattice)
    def wrapper(*args, **kwargs) -> str:

        lattice = deepcopy(orig_lattice)

        lattice.build_graph(*args, **kwargs)

        # Serializing the transport graph and then passing it to the Result object
        lattice.transport_graph = lattice.transport_graph.serialize()

        pickled_res = pickle.dumps(Result(lattice, lattice.metadata["results_dir"]))

        r = requests.post(
            SUBMIT_DISPATCH_QUEUER_ADDR, files={"result_pkl_file": BytesIO(pickled_res)}
        )
        r.raise_for_status()

        # Returns assigned dispatch id
        return r.json()["dispatch_id"]

    return wrapper


def get_result(dispatch_id: str, download=False):
    response = requests.get(
        get_svc_uri.ResultsURI().get_route(f"workflow/results/{dispatch_id}"), stream=True
    )
    response.raise_for_status()

    if not download:
        return pickle.loads(response.content)

    filename = f"result_{dispatch_id}.pkl"
    with open(filename, "wb") as f:
        f.write(response.content)

    return filename
