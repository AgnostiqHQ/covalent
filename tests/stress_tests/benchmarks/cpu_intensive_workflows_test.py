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
