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

import covalent as ct

N = 8
STALL = 1e6
X = 50


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


print(f"Number of electrons: {n_electrons}")
print(f"Execution time taken: {execution_time_taken}")


# with plt.xkcd():
#     plt.plot(n_electrons, execution_time_taken)
#     plt.xlabel("number of electrons")
#     plt.ylabel("execution time for each workflow")

# plt.show()
