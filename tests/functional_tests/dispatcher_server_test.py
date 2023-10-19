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
import covalent._results_manager.results_manager as rm


def test_dispatcher_server():
    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def add(x, y):
        import random
        import time

        time.sleep(random.choice([1, 2]))
        return x + y

    @ct.lattice
    def pipeline(a, b):
        res_1 = add(x=a, y=b)
        return identity(x=res_1)

    # After the dispatcher server has been started, you can run the following
    dispatch_id = ct.dispatch(pipeline)(a=2, b=1)
    assert dispatch_id is not None

    # Wait for it to complete
    result = ct.get_result(dispatch_id, wait=True)
    assert result is not None

    assert result.start_time is not None
    assert result.end_time is not None
    assert result.end_time > result.start_time
    assert result.status == ct.status.COMPLETED
    assert result.result == 3

    rm._delete_result(dispatch_id)
