import requests
from app.core.get_svc_uri import DispatcherURI

dispatch_id = "pog_dispatch_id"
url = DispatcherURI().get_route(f"workflow/{dispatch_id}")

resp = requests.post(url=url)
resp.raise_for_status()
print(resp.json())
