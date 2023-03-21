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
import pytest

import covalent as ct
from covalent._shared_files.util_classes import Status


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_matrix_multiplication(benchmark, iteration):
    run_benchmark = benchmark[0]
    logger = benchmark[1]
    arraysizes = [128, 256, 512, 1024]

    @ct.electron
    def create_matrix(arraysize: int):
        return np.random.random((arraysize, arraysize))

    @ct.electron
    def matrix_multiply(a: np.ndarray, b: np.ndarray):
        return np.matmul(a, b)

    @ct.lattice
    def matrix_multiplication(arraysizes):
        for arraysize in arraysizes:
            a = create_matrix(arraysize)
            b = create_matrix(arraysize)
            matrix_multiply(a, b)
        arraysizes = [256, 512, 1024]

    results, status = run_benchmark(iteration, matrix_multiplication, *[arraysizes])
    logger.debug(results.dict())

    assert status == Status("COMPLETED")
