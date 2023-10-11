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


import covalent as ct
from covalent._dispatcher_plugins.local import LocalDispatcher

dispatcher = LocalDispatcher()


def test_local_dispatcher_dispatch():
    """Tests whether the local dispatcher can dispatch a workflow successfully."""

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow(x, y):
        res = add(x, y)
        return add(res, y)

    dispatch_id = dispatcher.dispatch(workflow)(1, 2)
    result = ct.get_result(dispatch_id, wait=True)
    assert result.result == 5

    assert isinstance(dispatch_id, str)


def test_local_dispatcher_dispatch_sync():
    """Tests whether the local dispatcher can synchronously dispatch a workflow successfully."""

    @ct.electron
    def add(a, b):
        return a + b

    @ct.lattice
    def workflow(x, y):
        res = add(x, y)
        return add(res, y)

    result = dispatcher.dispatch_sync(workflow)(1, 2)
    assert result.result == 5
