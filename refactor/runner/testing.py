import json
import uuid
from pprint import pprint

import cloudpickle as pickle
import requests

import covalent as ct
from covalent._results_manager.result import Result
from covalent.executor import _executor_manager

dispatch_id = str(uuid.uuid4())

url = f"http://localhost:8000/api/v0/workflow/{dispatch_id}/tasks"


@ct.electron
def task_1(a):
    return a**2


@ct.electron
def task_2(a, b):
    return a * b


@ct.lattice
def workflow(x, y):
    res_1 = task_1(x + 2)
    res_2 = task_2(x, y)

    return res_1, res_2


workflow.build_graph(2, 10)

result_object = Result(workflow, workflow.metadata["results_dir"])
result_object._initialize_nodes()

tasks = [
    {
        "task_id": 0,
        "func": result_object.lattice.transport_graph.get_node_value(0, "function"),
        "args": [2 + 2],
        "kwargs": {},
        "executor": result_object.lattice.transport_graph.get_node_value(0, "metadata")[
            "executor"
        ],
        "results_dir": result_object.results_dir,
    },
    {
        "task_id": 2,
        "func": result_object.lattice.transport_graph.get_node_value(2, "function"),
        "args": [2, 10],
        "kwargs": {},
        "executor": result_object.lattice.transport_graph.get_node_value(2, "metadata")[
            "executor"
        ],
        "results_dir": result_object.results_dir,
    },
]


response = requests.post(url=url, data=pickle.dumps(tasks))
response.raise_for_status()

left_task_ids = response.json()
print(left_task_ids)
