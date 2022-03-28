from io import BytesIO

import cloudpickle as pickle
import requests

import covalent as ct
from covalent._results_manager.result import Result

dispatch_id = "new_dispatch"
url_endpoint = "http://localhost:8002/api/v0/workflow/results/"


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
result_object = Result(
    lattice=workflow, results_dir=workflow.metadata["results_dir"], dispatch_id=dispatch_id
)
result_object._lattice.transport_graph = result_object._lattice.transport_graph.serialize()

print("Dispatch ID before posting: ", result_object.dispatch_id)

# with open(f"./kekw/{dispatch_id}/result.pkl", "rb") as pkl_file:
#     response = requests.post(url=url_endpoint, files={"result_pkl_file": pkl_file})

response = requests.post(
    url=url_endpoint, files={"result_pkl_file": BytesIO(pickle.dumps(result_object))}
)

response.raise_for_status()
print(response.text)
