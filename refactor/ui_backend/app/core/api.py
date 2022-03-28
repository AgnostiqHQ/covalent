import os
from urllib.parse import urljoin

import requests

from refactor.queuer.app.core.config import settings


class APIService:
    def __init__(self, BASE_URI: str):
        if BASE_URI[len(BASE_URI) - 1] != "/":
            BASE_URI = f"{BASE_URI}/"
        self.BASE_URI = BASE_URI

    def _get_route(self, path: str):
        return urljoin(self.BASE_URI, path)

    def _format(self, response, raw):
        if raw:
            return response
        else:
            return response.json()

    def post(self, path, json={}, params={}, data={}, files={}):
        route = self._get_route(path)
        return self._format(requests.post(route, json=json, params=params, data=data, files=files))

    def get(self, path, params={}, raw=False):
        route = self._get_route(path)
        return self._format(requests.get(route, params=params), raw)

    def delete(self, path, params={}):
        route = self._get_route(path)
        return self._format(requests.delete(route, params=params))

    def patch(self, path, json={}, params={}, data={}):
        route = self._get_route(path)
        return self._format(requests.patch(route, json=json, params=params, data=data))

    def put(self, path, json={}, params={}, data={}):
        route = self._get_route(path)
        return self._format(requests.put(route, json=json, params=params, data=data))


class DataService(APIService):
    def __init__(self):
        print("Settings:")
        print(settings)
        super().__init__(settings.DATA_OS_SVC_HOST_URI)

    async def get_result(self, dispatch_id: str):
        # dirname = os.path.dirname(__file__)
        # filename = os.path.join(dirname, './result.pkl')
        # with open(filename, 'rb') as f:
        #     return f.read()
        # res = self.get(f"api/v0/workflow/results/{dispatch_id}", raw=True)
        res = requests.get(f"http://localhost:8002/api/v0/workflow/results/{dispatch_id}")

        print("Printing content now")
        print(res.content)
        return res.content

    async def create_result(self, result_pkl_file: bytes):
        return self.post("workflow/results", files={"result_pkl_file": result_pkl_file})
