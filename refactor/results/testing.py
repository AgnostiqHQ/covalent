import time

import cloudpickle as pickle
import requests

import covalent as ct
from covalent._results_manager.result import Result

dispatch_id = "b924c80f-03a8-436f-916d-26c859b4eb4c"

url = "http://localhost:8002/api/v0/workflow/results/"


@ct.electron
def task_1(a):
    import time

    time.sleep(10)
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
result_object = Result(
    lattice=workflow, results_dir=workflow.metadata["results_dir"], dispatch_id=dispatch_id
)
# result_object._lattice.transport_graph = result_object._lattice.transport_graph.serialize()
result_object._initialize_nodes()


result_object.save(directory="./sampling/")

print("Dispatch ID before posting: ", result_object.dispatch_id)

with open(f"./sampling/{dispatch_id}/result.pkl", "rb") as pkl_file:
    response = requests.post(url=url, files={"result_pkl_file": pkl_file})

response.raise_for_status()
print(response.text)

# time.sleep(2)

# response = requests.get(url=f"{url}{dispatch_id}")
# response.raise_for_status()

# new_result_object = pickle.loads(response.content)

# print(new_result_object.dispatch_id)
