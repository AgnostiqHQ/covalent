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
from covalent._shared_files.util_classes import Status


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_fully_vertical_add_workflow(benchmark, iteration):
    run_benchmark, logger = benchmark

    @ct.electron
    def add(x: int, y: int):
        return x + y

    @ct.lattice
    def vertical_add_workflow(N: int):
        for i in range(N):
            if i == 0:
                r1 = add(1, 1)
            else:
                r1 = add(r1, 1)
        return r1

    result, status = run_benchmark(iteration, vertical_add_workflow, *[50])
    logger.debug(result.dict())

    assert status == Status("COMPLETED")


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_fully_vertical_multiply_workflow(benchmark, iteration):
    run_benchmark, logger = benchmark

    @ct.electron
    def multiply(x: int, y: int):
        return x + y

    @ct.lattice
    def vertical_multiply_workflow(N: int):
        for i in range(N):
            if i == 0:
                r1 = multiply(2, 2)
            else:
                r1 = multiply(r1, 2)
        return r1

    result, status = run_benchmark(iteration, vertical_multiply_workflow, *[50])
    logger.debug(result.dict())

    assert status == Status("COMPLETED")
