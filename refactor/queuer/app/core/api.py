import os
import requests

from urllib.parse import urljoin

class APIService():

    def __init__(self, BASE_URI: str):
        if BASE_URI[len(BASE_URI)-1] != "/":
            BASE_URI = f"{BASE_URI}/"
        self.BASE_URI = BASE_URI
    
    def _get_route(self, path: str):
        return urljoin(self.BASE_URI, path)

    def _format(self, response):
        return response.json()

    def post(self, path, json = {}, params = {},  data={}, files={}):
        route = self._get_route(path)
        return self._format(requests.post(route, json=json, params=params,  data=data, files=files))
    
    def get(self, path, params = {}):
        route = self._get_route(path)
        return self._format(requests.get(route, params=params))
    
    def delete(self, path, params = {}):
        route = self._get_route(path)
        return self._format(requests.delete(route, params=params))
    
    def patch(self, path, json = {}, params = {},  data={}):
        route = self._get_route(path)
        return self._format(requests.patch(route, json=json, params=params,  data=data))
    
    def put(self, path, json = {}, params = {}, data={}):
        route = self._get_route(path)
        return self._format(requests.put(route, json=json, params=params,  data=data))


class DataService(APIService):
    def __init__(self):
        super().__init__(os.environ.get("DATA_OS_SVC_HOST_URI"))

    async def create_result(self, result_pkl_file: bytes):
        return self.post('fs/upload', files={
            "result_pkl_file": result_pkl_file
        })
