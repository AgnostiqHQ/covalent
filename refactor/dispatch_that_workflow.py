import requests

dispatch_id = "new_dispatch"
url_endpoint = f"http://localhost:8003/api/v0/workflow/{dispatch_id}"

response = requests.post(url=url_endpoint)
response.raise_for_status()
print(response.text)
