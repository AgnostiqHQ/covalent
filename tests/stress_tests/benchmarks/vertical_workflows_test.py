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
