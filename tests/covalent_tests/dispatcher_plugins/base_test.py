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

import pytest

from covalent._dispatcher_plugins.base import BaseDispatcher
from covalent._results_manager.result import Result


def test_dispatcher_creation_with_dispatch_functions():
    """
    Test that the dispatcher class can be created with the
    `dispatch` and `dispatch_sync` methods.
    """

    class TestDispatcher(BaseDispatcher):
        """
        A test dispatcher class.
        """

        def dispatch(self) -> None:
            """
            Test dispatch wrapper.
            """

            pass

        def dispatch_sync(self) -> Result:
            """
            Test dispatch_sync wrapper.
            """

            pass

    assert TestDispatcher()


def test_dispatcher_creation_wo_dispatch_functions():
    """
    Test that the dispatcher class cannot be created without the
    `dispatch` and `dispatch_sync` method.
    """

    class TestDispatcher(BaseDispatcher):
        """
        A test dispatcher class.
        """

    with pytest.raises(TypeError):
        TestDispatcher()
