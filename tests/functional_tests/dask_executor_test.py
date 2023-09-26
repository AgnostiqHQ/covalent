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

import covalent as ct
from covalent._results_manager import Result


def start_dask_cluster():
    from dask.distributed import LocalCluster

    cluster = LocalCluster()

    return cluster.scheduler_address


@pytest.mark.skip(reason="Stalling the functional test pipeline")
def test_dask_executor():
    from covalent.executor import DaskExecutor

    scheduler_address = start_dask_cluster()
    dask_executor = DaskExecutor(scheduler_address=scheduler_address)

    @ct.electron(executor=dask_executor)
    def identity(x):
        return x

    @ct.electron(executor=dask_executor)
    def combine(x):
        return sum(x)

    @ct.lattice
    def workflow(n):
        vals = []
        result = 1
        nodes = range(n)

        for i in nodes:
            for _ in nodes:
                if i == 0:
                    vals.append(identity(1))
                else:
                    vals.append(identity(result))
            result = combine(vals)

        return result, vals

    dispatcher = ct.dispatch(workflow)

    n = 10
    dispatch_id = dispatcher(n=n)
    print(f"Dispatching with dispatch_id: {dispatch_id}")

    result = ct.get_result(dispatch_id=dispatch_id, wait=True)

    time_taken = (result.end_time - result.start_time).total_seconds()
    print(f"Time taken: {time_taken}")

    assert result.status == Result.COMPLETED
