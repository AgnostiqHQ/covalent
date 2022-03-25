import requests

dispatch_id = "my_new_world"

task_id = 2

url_endpoint = f"http://localhost:8005/api/v0/ui/workflow/{dispatch_id}/task/{task_id}"

response = requests.put(url=url_endpoint)
response.raise_for_status()

print(response.text)
