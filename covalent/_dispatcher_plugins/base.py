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
