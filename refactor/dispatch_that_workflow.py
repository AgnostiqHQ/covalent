import requests

dispatch_id = "my_new_world"
url_endpoint = f"http://localhost:8003/api/v0/workflow/{dispatch_id}"

response = requests.post(url=url_endpoint)
response.raise_for_status()
print(response.text)
