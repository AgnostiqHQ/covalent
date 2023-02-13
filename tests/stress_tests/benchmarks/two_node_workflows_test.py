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
def test_add_multiply_workflow(benchmark, iteration: int):
    print(iteration)
    run_benchmark = benchmark[0]
    logger = benchmark[1]

    @ct.electron
    def add(x, y):
        return x + y

    @ct.electron
    def multiply(x, y):
        return x * y

    @ct.lattice
    def add_multiply_workflow(x, y):
        r1 = add(x, y)
        r2 = multiply(r1, y)
        return r2

    metrics, dispatch_status = run_benchmark(iteration, add_multiply_workflow, *[1, 2])
    logger.debug(metrics.dict())

    assert dispatch_status == Status("COMPLETED")
