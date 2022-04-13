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


import time

import covalent as ct
from refactor.executor.executor_plugins.local import LocalExecutor

executor = LocalExecutor()


@ct.electron(executor=executor)
def task_1(x):
    return x**2


@ct.electron(executor=executor)
def subtask(a, b):
    return a**b


@ct.electron(executor=executor)
@ct.lattice
def task_2(y, z):
    return subtask(y, z)


@ct.lattice(executor=executor)
def workflow(a):

    task_2(a, 10)

    return task_1(a)


dispatch_id = ct.dispatch(workflow)(3)

print(dispatch_id)

# time.sleep(3)

# No matter what dispatch id is sent, it returns from the last one only
# print(interface_with_covalent.get_result("f659c221-362f-4b91-8e69-b10e3b8543f0"))
