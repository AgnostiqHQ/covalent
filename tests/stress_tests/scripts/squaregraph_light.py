# Workflow with a large graph, all lightweight electrons
# Transport graph looks like a feedforward neural network
# comprising of fully-connected layers.
# e e e e...
# e e e e...
# e e e e...
# with each task depending on all the tasks in the previous layer

import os
import time

import yaml

import covalent as ct

benchmark_name = "squaregraph_light"
benchmark_dir = f"benchmark_results/{benchmark_name}/current"

if not os.path.isdir(benchmark_dir):
    os.makedirs(benchmark_dir)

# NOTE: graph size is width^2
widths = [2**i for i in range(6)]
trials_per_width = 3


# Square feedforward-type, fully connected graph
# e e e
# e e e
# e e e


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
    tasks = [[sample_task for i in range(w)] for i in range(w)]
    deps = []
    for i in range(w - 1):
        deps.append([[j for j in range(w)] for j in range(w)])
    for i in range(trials_per_width):
        workflow = ct.lattice(feedforward_workflow)

        start = time.time()
        res = workflow(tasks, deps)
        end = time.time()

        outfile = f"{benchmark_dir}/no_ct_width_{w}_trial_{i}"
        with open(outfile, "w") as f:
            yaml.dump(
                {
                    "test": benchmark_name,
                    "ct": False,
                    "height": w,
                    "width": w,
                    "runtime": end - start,
                },
                f,
            )
        print("(w/o ct) runtime for width {}: {} seconds".format(w, end - start))

time.sleep(3)

# With covalent
for w in widths:
    tasks = [[sample_task for i in range(w)] for i in range(w)]
    deps = []
    for i in range(w - 1):
        deps.append([[j for j in range(w)] for j in range(w)])
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
                    "height": w,
                    "width": w,
                    "runtime": (result.end_time - result.start_time).total_seconds(),
                },
                f,
            )
        print("runtime for width {}: {} seconds".format(w, result.end_time - result.start_time))
