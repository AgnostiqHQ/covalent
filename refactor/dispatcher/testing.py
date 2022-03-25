import requests

dispatch_id = "pog_dispatch_id"
url = f"http://localhost:8000/api/v0/workflow/{dispatch_id}"

resp = requests.post(url=url)
resp.raise_for_status()
print(resp.json())
