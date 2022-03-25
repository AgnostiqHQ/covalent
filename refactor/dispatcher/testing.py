import requests

dispatch_id = "helloworld"
url = f"http://localhost:8000/api/v0/workflow/{dispatch_id}"

resp = requests.post(url=url)
print(resp.json())
