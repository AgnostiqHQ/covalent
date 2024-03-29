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

import random

import pytest

import covalent as ct
from covalent._shared_files.util_classes import Status


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_primality_test(benchmark, iteration):
    run_benchmark = benchmark[0]
    logger = benchmark[1]

    @ct.electron
    def is_prime(n: int) -> bool:
        """Primality test using 6k+-1 optimization."""
        if n <= 3:
            return n > 1
        if not n % 2 or not n % 3:
            return False
        i = 5
        stop = int(n**0.5)
        while i <= stop:
            if not n % i or not n % (i + 2):
                return False
            i += 6
        return True

    @ct.lattice
    def primality_tests(nums_to_test):
        res = []
        for i in nums_to_test:
            entry = {}
            entry["num"] = i
            entry["is_prime"] = is_prime(i)
            res.append(entry)
        return res

    nums_to_test = [random.randint(1000, 10000) for i in range(50)]

    results, status = run_benchmark(iteration, primality_tests, *[nums_to_test])
    logger.debug(results.dict())

    assert status == Status("COMPLETED")
