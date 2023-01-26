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

from abc import ABC, abstractmethod
from typing import Any

from .._results_manager.result import Result
from .._workflow.lattice import Lattice


class BaseDispatcher(ABC):
    """
    The base dispatcher class to allow defining custom dispatchers.
    Subclassed dispatchers must implement the `dispatch` method and
    `dispatch_sync` methods. These dispatchers act as the interface
    to the covalent dispatcher server and using the `dispatch` method
    will allow the user to submit jobs to the dispatcher server.
    """

    def __init__(self) -> None:
        pass

    @abstractmethod
    def dispatch(self, lattice: Lattice, custom_variables: Any) -> None:
        """
        Dispatch a lattice to the dispatcher server.
        """

        pass

    @abstractmethod
    def dispatch_sync(self, lattice: Lattice, custom_variables: Any) -> Result:
        """
        Dispatch a lattice to the dispatcher server and wait for the results.
        """

        pass
