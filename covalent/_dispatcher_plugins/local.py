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
from typing import Callable

import cloudpickle as pickle
import requests

from .._results_manager.result import Result
from .._results_manager.results_manager import get_result
from .._shared_files.config import get_config
from .._workflow.lattice import Lattice
from .base import BaseDispatcher


class LocalDispatcher(BaseDispatcher):
    """
    Local dispatcher which sends the workflow to the locally running
    dispatcher server.
    """

    @staticmethod
    def dispatch(
        orig_lattice: Lattice,
        dispatcher_addr: str = get_config("dispatcher.address")
        + ":"
        + str(get_config("dispatcher.port")),
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

            # Serializing the transport graph and then passing it to the Result object
            lattice.transport_graph = lattice.transport_graph.serialize()

            pickled_res = pickle.dumps(Result(lattice, lattice.metadata["results_dir"]))
            test_url = f"http://{dispatcher_addr}/api/submit"

            r = requests.post(test_url, data=pickled_res)
            r.raise_for_status()
            return r.content.decode("utf-8").strip().replace('"', "")

        return wrapper

    @staticmethod
    def dispatch_sync(
        lattice: Lattice,
        dispatcher_addr: str = get_config("dispatcher.address")
        + ":"
        + str(get_config("dispatcher.port")),
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
                LocalDispatcher.dispatch(lattice, dispatcher_addr)(*args, **kwargs),
                lattice.metadata["results_dir"],
                wait=True,
            )

        return wrapper
