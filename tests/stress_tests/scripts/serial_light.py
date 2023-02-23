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

# Workflow with a single chain of lightweight tasks
# Graph consists of a single chain
# e
# e
# e
# .
# .
# .

import os
import time

import yaml

import covalent as ct

benchmark_name = "serial_light"
benchmark_dir = f"benchmark_results/{benchmark_name}/current"

if not os.path.isdir(benchmark_dir):
    os.makedirs(benchmark_dir)

widths = [2**i for i in range(10)]
trials_per_width = 3


# Single layer of independent electrons
# e e e ...


def sample_task(*args, **kwargs):
    return 1


# General workflow with a feedforward transport graph
# Each task can depend on any number of tasks in the previous layer
def feedforward_workflow(tasks, predecessors):
    """General workflow with a feedforward-type transport graph.

    The graph is expressed as a list of task lists. Each task can
    depend on any number of tasks in the previous layer as specified
    by `predecessors`. The top layer of tasks is assumed to accept no
    inputs. For instance,

    tasks = [ [task00, task01], [task10, task11], [task20, task21]]
    predecessors = [ [[0, 1], [0]], [[1], [1]] ]

    expresses a transport graph in which task10 depends on task00 and task01,
    task11 depends on task00, and task20 and task21 each depend only task11.

    """
    electrons = [[ct.electron(tasks[0][j])() for j in range(len(tasks[0]))]]
    for i in range(1, len(tasks)):
        next_electrons = []
        for j in range(len(tasks[i])):
            args = [electrons[i - 1][k] for k in predecessors[i - 1][j]]
            next_electrons.append(ct.electron(tasks[i][j])(*args))
        electrons.append(next_electrons)
    return 1


# Without covalent
for w in widths:
    tasks = [[sample_task] for i in range(w)]
    deps = [[[0]] for i in range(w - 1)]
    for i in range(trials_per_width):
        workflow = ct.lattice(feedforward_workflow)

        start = time.time()
        res = workflow(tasks, deps)
        end = time.time()

        outfile = f"{benchmark_dir}/no_ct_width_{w}_trial_{i}"
        with open(outfile, "w") as f:
            yaml.dump({"test": benchmark_name, "ct": False, "width": w, "runtime": end - start}, f)
        print("(w/o ct) runtime for width {}: {} seconds".format(w, end - start))

time.sleep(3)

# With covalent
for w in widths:
    tasks = [[sample_task] for i in range(w)]
    deps = [[[0]] for i in range(w - 1)]
    for i in range(trials_per_width):
        workflow = ct.lattice(feedforward_workflow)

        result = ct.dispatch_sync(workflow)(tasks, deps)

        assert result.status == ct.status.COMPLETED

        outfile = f"{benchmark_dir}/{result.dispatch_id}"
        with open(outfile, "w") as f:
            yaml.dump(
                {
                    "test": benchmark_name,
                    "ct": True,
                    "dispatch_id": result.dispatch_id,
                    "width": w,
                    "runtime": (result.end_time - result.start_time).total_seconds(),
                },
                f,
            )
        print("runtime for width {}: {} seconds".format(w, result.end_time - result.start_time))
