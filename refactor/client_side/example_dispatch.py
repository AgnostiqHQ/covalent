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


import numpy as np
from sklearn.preprocessing import SplineTransformer

import covalent as ct


@ct.electron
def task_1():
    X = np.arange(5).reshape(5, 1)
    spline = SplineTransformer(degree=2, n_knots=3)
    return spline.fit_transform(X)


@ct.electron
def subtask(a, b):
    return a**b


@ct.electron
@ct.lattice
def task_2(y, z):
    return subtask(y, z)


@ct.lattice
def workflow(a):

    task_2(a, 10)

    return task_1(a)


dispatch_id = ct.dispatch(workflow)(3)

print(dispatch_id)

result = ct.get_result(dispatch_id=dispatch_id, wait=True)

print(result)
