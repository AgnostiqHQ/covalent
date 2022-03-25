import cloudpickle as pickle
import requests

dispatch_id = "b924c80f-03a8-436f-916d-26c859b4eb4c"

url = "http://localhost:8002/api/v0/workflow/results/"

task_result = {
    "node_id": 0,
    "output": 5,
}

response = requests.put(url=f"{url}{dispatch_id}", files={"task": pickle.dumps(task_result)})
response.raise_for_status()

print(response.text)
