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
