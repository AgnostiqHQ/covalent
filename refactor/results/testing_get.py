import cloudpickle as pickle
import requests

dispatch_id = "b924c80f-03a8-436f-916d-26c859b4eb4c"

url = "http://localhost:8002/api/v0/workflow/results/"


response = requests.get(url=f"{url}{dispatch_id}")
response.raise_for_status()

new_result_object = pickle.loads(response.content)

print(new_result_object)
