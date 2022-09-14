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
