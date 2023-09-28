# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Client Template"""

from enum import Enum
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient


class MethodType(Enum):
    """API methods"""

    GET = "get"
    POST = "post"
    PUT = "put"


class TestClientTemplate:
    """Custom test client"""

    api_path: str = ""
    app: FastAPI = None
    method_type: MethodType = MethodType.GET
    body_data: Dict = {}
    query_data: Dict = {}
    header: str = ""
    path: Dict = {}

    def build_query(self, api_path: str, path: dict, query: dict) -> str:
        """
        Build api path
        Args:
            api_path: API end point
            path: Path variables
            query: Query variables
        Returns:
            api path
        """
        api_path = api_path.format(*path.values()) if path is not None else api_path
        if query:
            api_path += "?"
            for idx_id, i in enumerate(query):
                api_path += "&" if idx_id != 0 else ""
                api_path += f"{i}={query[i]}"
        return api_path

    def __call__(
        self,
        api_path: str,
        app: FastAPI,
        method_type: MethodType,
        body_data: Dict = None,
        query_data: Dict = None,
        header: str = None,
        path: Dict = None,
    ) -> Any:
        self.api_path = self.build_query(api_path=api_path, query=query_data, path=path)
        self.app = app
        self.method_type = method_type
        self.body_data = body_data
        self.header = header

        return self.api_call_method()

    def api_call_method(self):
        """Test client"""
        with TestClient(self.app) as client:
            if self.method_type == MethodType.POST:
                return client.post(self.api_path, json=self.body_data, headers=self.header)
            else:
                return client.get(self.api_path)
