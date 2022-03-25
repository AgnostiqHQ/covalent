import cloudpickle as pickle
import requests

dispatch_id = "my_new_world"

url = "http://localhost:8002/api/v0/workflow/results/"


response = requests.get(url=f"{url}{dispatch_id}")
response.raise_for_status()

new_result_object = pickle.loads(response.content)

print(new_result_object)
