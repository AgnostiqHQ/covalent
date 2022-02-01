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

import inspect
from copy import deepcopy
from functools import wraps

import cloudpickle as pickle
import requests

from .._results_manager.result import Result
from .._results_manager.results_manager import get_result
from .._workflow.lattice import Lattice
from .base import BaseDispatcher


class LocalDispatcher(BaseDispatcher):
    @staticmethod
    def dispatch(orig_lattice: Lattice) -> str:
        @wraps(orig_lattice)
        def wrapper(*args, **kwargs) -> str:

            lattice = deepcopy(orig_lattice)

            if lattice.workflow_function:
                kwargs.update(
                    dict(zip(list(inspect.signature(lattice.workflow_function).parameters), args))
                )

            lattice.build_graph(**kwargs)

            # Serializing the transport graph and then passing it to the Result object
            lattice.transport_graph = lattice.transport_graph.serialize()

            pickled_res = pickle.dumps(Result(lattice, lattice.metadata["results_dir"]))
            test_url = "http://" + lattice.metadata["dispatcher"] + "/api/submit"

            r = requests.post(test_url, data=pickled_res)
            r.raise_for_status()
            return r.content.decode("utf-8").strip().replace('"', "")

        return wrapper

    @staticmethod
    def dispatch_sync(lattice: Lattice) -> Result:
        @wraps(lattice)
        def wrapper(*args, **kwargs):

            return get_result(
                LocalDispatcher.dispatch(lattice)(*args, **kwargs),
                lattice.metadata["results_dir"],
                wait=True,
            )

        return wrapper
