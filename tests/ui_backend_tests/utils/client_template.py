from enum import Enum
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.testclient import TestClient


class MethodType(Enum):
    GET = "get"
    POST = "post"
    PUSH = "push"
    PUT = "put"


class TestClientTemplate:

    path: str = None
    app: FastAPI = None
    method_type: MethodType = MethodType.GET
    body_data: Dict = (None,)
    query_data: Dict = (None,)
    header: str = (None,)

    def build_query(self, path, query):

        path += "?"
        for id, i in enumerate(query):
            path += "&" if id != 0 else ""
            path += f"{i}={query[i]}"
        return path

    def __call__(
        self,
        path: str,
        app: FastAPI,
        method_type: MethodType,
        body_data: Dict = None,
        query_data: Dict = None,
        header: str = None,
    ) -> Any:
        self.path = (
            path
            if (query_data is None) or not (query_data)
            else self.build_query(path=path, query=query_data)
        )
        self.app = app
        self.method_type = method_type
        self.body_data = body_data
        self.header = header

        return self.api_call_method()

    def api_call_method(self):

        with TestClient(self.app) as client:
            if self.method_type == MethodType.POST:
                return client.post(self.path, json=self.body_data, headers=self.header)
            else:
                return client.get(self.path)
