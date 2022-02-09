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

"""Covalent context managers."""

import threading
from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

if TYPE_CHECKING:
    from .._shared_files.util_classes import DispatchInfo
    from .._workflow.lattice import Lattice


class ActiveLatticeManager(threading.local):
    """
    The active lattice manager is used to determine whether an electron is being "called"
    from inside or outside a lattice. The lattice "claims" itself as active before electrons
    are called and "unclaims" itself afterwards. The claim mechanism is managed as a standard
    python context manager. The electron will get_active_lattice from within the context and
    bind itself to the transport_graph. The electron should NOT retain any part of the lattice
    or transport graph.

    Since threading.local is being subclassed here, this class is thread-safe.
    """

    def __init__(self) -> None:
        self._active_lattice = None

    def get_active_lattice(self) -> "Lattice":
        """
        Return the active lattice.

        Args:
            None

        Returns:
            active_lattice: The active lattice.
        """

        return self._active_lattice

    @contextmanager
    def claim(self, lattice: "Lattice") -> None:
        """
        Claim the given lattice as active.

        Args:
            lattice: The lattice to claim.

        Returns:
            None

        Raises:
            ValueError: If the lattice is already claimed.
            ValueError: If an attempt was made to unset lattice when it wasn't even set.
        """

        if self._active_lattice:
            raise ValueError(
                f"There is already an active lattice: {self._active_lattice.workflow_function.__name__}"
            )
        self._active_lattice = lattice
        try:
            yield None
        finally:
            if not self._active_lattice:
                raise ValueError("Cannot unset the active lattice if nothing is set.")
            self._active_lattice = None


class ActiveDispatchInfoManager:
    """
    The active dispatch info manager is used to maintain a single instance of dispatch information
    which can be used by any of the executors or when required inside the electron execution.
    For example, the lattice level details, such as the total budget assigned, or total time allotted
    for the whole lattice execution, are not accessible inside the electron at the time of dispatching.
    If they are required at the time of electron execution, this manager is used to provide access
    to information like that.
    """

    def __init__(self) -> None:
        self._active_dispatch_info = None

    def get_active_dispatch_info(self) -> "DispatchInfo":
        """
        Returns the active dispatch info.

        Args:
            None

        Returns:
            active_dispatch_info: The active dispatch info.
        """

        return self._active_dispatch_info

    @contextmanager
    def claim(self, dispatch_info: "DispatchInfo") -> Generator:
        """
        Claims the given dispatch info as active.

        Args:
            dispatch_info: The dispatch info object to claim.

        Returns:
            Returns a generator, which gets converted into a contextmanager.
        """

        self._active_dispatch_info = dispatch_info
        yield
        self._active_dispatch_info = None


active_lattice_manager = ActiveLatticeManager()
active_dispatch_info_manager = ActiveDispatchInfoManager()
