# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.
import logging
import os
import sqlite3
from typing import Optional, Tuple, Union
from urllib.parse import urljoin

import requests
from app.core.config import settings
from app.core.get_svc_uri import DataURI
from fastapi import HTTPException


class APIService:
    def __init__(self, BASE_URI: str):
        if BASE_URI[len(BASE_URI) - 1] != "/":
            BASE_URI = f"{BASE_URI}/"
        self.BASE_URI = BASE_URI

    def _get_route(self, path: str):
        return urljoin(self.BASE_URI, path)

    def _format(self, response, content=False):
        if response.status_code >= 400:
            error_body = response.json()
            raise HTTPException(status_code=response.status_code, detail=error_body["detail"])
        if content:
            return response.content
        return response.json()

    def post(self, path, json={}, params={}, data={}, files={}):
        route = self._get_route(path)
        return self._format(requests.post(route, json=json, params=params, data=data, files=files))

    def get(self, path, params={}, stream=False, content=False):
        route = self._get_route(path)
        return self._format(requests.get(route, params=params, stream=stream), content)

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
        super().__init__(str(DataURI().get_base_url()))

    async def download(self, filename: str):
        return self.get(
            "/api/v0/fs/download", params={"file_location": filename}, stream=True, content=True
        )

    async def upload(self, result_pkl_file: bytes):
        return self.post(
            "/api/v0/fs/upload",
            files=[("file", ("result.pkl", result_pkl_file, "application/octet-stream"))],
        )
