import json
from enum import Enum
from os.path import abspath, dirname
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
    input_data: Dict
    header: str

    def __call__(
        self,
        path: str,
        app: FastAPI,
        method_type: MethodType,
        input_data: Dict = None,
        header: str = None,
    ) -> Any:
        self.path = path
        self.app = app
        self.method_type = method_type
        self.input_data = input_data
        self.header = header

        return self.api_call_method()

    def api_call_method(self):

        with TestClient(self.app) as client:
            if self.method_type == MethodType.POST:
                return client.post(self.path, data=self.input_data, headers=self.header)
            else:
                return client.get(self.path)
