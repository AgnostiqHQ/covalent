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


# Run using cova 0.110.2.post1 from PyPI

import covalent as ct
from covalent.executor import LocalExecutor

assert ct.__version__ == "0.110.2"

le = LocalExecutor()


class TestClass:
    def __init__(self, x: list):
        self.x = x[0]


@ct.electron(executor=le)
def task_0(x):
    return TestClass(x)


@ct.electron(executor=le)
def task_1():
    return [[1, 2], 3]


@ct.electron
def task(x):
    return x


@ct.electron
@ct.lattice
def sub_workflow(x):
    return task(x)


@ct.lattice(executor=le)
def workflow(z, zz):
    # task node 0, collection node 1, parameters 2, 3
    res = task_0(z)

    # attribute node 4
    x = res.x

    # sublattice node 5
    sub_res = sub_workflow(x)

    # task node 6, generator nodes 7, 8
    res1, res2 = task_1()

    # subscript node 9
    y = res1[0]

    return 1


dispatch_id = ct.dispatch(workflow)([1, 2], zz=2)
print(dispatch_id)
result_object = ct.get_result(dispatch_id, wait=True)
print(result_object.result)
