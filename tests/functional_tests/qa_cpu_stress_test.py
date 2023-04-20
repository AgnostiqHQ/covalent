# Copyright 2023 Agnostiq Inc.
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

"""CPU stress test."""

import covalent as ct

N = 8
STALL = 1e6
X = 50


def test_cpu_stress():
    """Stress test the CPU."""

    @ct.electron
    def cpu_workload(stall, x):
        i = 0
        while i < stall:
            x * x
            i += 1

    @ct.lattice
    def workflow(iterations, stall, x):
        for _ in range(iterations):
            cpu_workload(stall, x)

    n_electrons = [2**i for i in range(N)]
    execution_time_taken = []
    dispatch_ids = [ct.dispatch(workflow)(it, STALL, X) for it in n_electrons]

    for d_id in dispatch_ids:
        result = ct.get_result(d_id, wait=True)
        execution_time_taken.append((result.end_time - result.start_time).total_seconds())

    for time_taken in execution_time_taken:
        assert time_taken < 20
