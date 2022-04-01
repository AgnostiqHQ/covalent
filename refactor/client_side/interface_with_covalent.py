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
import requests

from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice

QUEUER_ADDR = "http://localhost:8000"


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
        test_url = f"{QUEUER_ADDR}/api/v0/submit/dispatch"

        r = requests.post(test_url, files={"result_pkl_file": BytesIO(pickled_res)})
        r.raise_for_status()
        return r.content.decode("utf-8").strip().replace('"', "")

    return wrapper


def get_result():
    pass
