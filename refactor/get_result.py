import cloudpickle as pickle
import requests

dispatch_id = "new_dispatch"

url = "http://localhost:8002/api/v0/workflow/results/"


response = requests.get(url=f"{url}{dispatch_id}")
response.raise_for_status()

new_result_object = pickle.loads(response.content)

print(new_result_object)
