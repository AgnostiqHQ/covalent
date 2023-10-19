# Copyright 2023 Agnostiq Inc.
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


"""API client"""

import json
import os
from typing import Dict

import requests
from requests.adapters import HTTPAdapter


class CovalentAPIClient:
    """Thin wrapper around Requests to centralize error handling."""

    def __init__(self, dispatcher_addr: str, adapter: HTTPAdapter = None, auto_raise: bool = True):
        self.dispatcher_addr = dispatcher_addr
        self.adapter = adapter
        self.auto_raise = auto_raise

    def prepare_headers(self, **kwargs):
        extra_headers = CovalentAPIClient.get_extra_headers()
        headers = kwargs.get("headers", {})
        if headers:
            kwargs.pop("headers")
        headers.update(extra_headers)
        return headers

    def get(self, endpoint: str, **kwargs):
        headers = self.prepare_headers(**kwargs)
        url = self.dispatcher_addr + endpoint
        try:
            with requests.Session() as session:
                if self.adapter:
                    session.mount("http://", self.adapter)

                r = session.get(url, headers=headers, **kwargs)

            if self.auto_raise:
                r.raise_for_status()

        except requests.exceptions.ConnectionError:
            message = f"The Covalent server cannot be reached at {url}. Local servers can be started using `covalent start` in the terminal. If you are using a remote Covalent server, contact your systems administrator to report an outage."
            print(message)
            raise

        return r

    def put(self, endpoint: str, **kwargs):
        headers = self.prepare_headers()
        url = self.dispatcher_addr + endpoint
        try:
            with requests.Session() as session:
                if self.adapter:
                    session.mount("http://", self.adapter)

                r = session.put(url, headers=headers, **kwargs)

            if self.auto_raise:
                r.raise_for_status()
        except requests.exceptions.ConnectionError:
            message = f"The Covalent server cannot be reached at {url}. Local servers can be started using `covalent start` in the terminal. If you are using a remote Covalent server, contact your systems administrator to report an outage."
            print(message)
            raise

        return r

    def post(self, endpoint: str, **kwargs):
        headers = self.prepare_headers()
        url = self.dispatcher_addr + endpoint
        try:
            with requests.Session() as session:
                if self.adapter:
                    session.mount("http://", self.adapter)

                r = session.post(url, headers=headers, **kwargs)

            if self.auto_raise:
                r.raise_for_status()
        except requests.exceptions.ConnectionError:
            message = f"The Covalent server cannot be reached at {url}. Local servers can be started using `covalent start` in the terminal. If you are using a remote Covalent server, contact your systems administrator to report an outage."
            print(message)
            raise

        return r

    def delete(self, endpoint: str, **kwargs):
        headers = self.prepare_headers()
        url = self.dispatcher_addr + endpoint
        try:
            with requests.Session() as session:
                if self.adapter:
                    session.mount("http://", self.adapter)

                r = session.delete(url, headers=headers, **kwargs)

            if self.auto_raise:
                r.raise_for_status()
        except requests.exceptions.ConnectionError:
            message = f"The Covalent server cannot be reached at {url}. Local servers can be started using `covalent start` in the terminal. If you are using a remote Covalent server, contact your systems administrator to report an outage."
            print(message)
            raise

        return r

    @classmethod
    def get_extra_headers(headers: Dict) -> Dict:
        # This is expected to be a JSONified dictionary
        data = os.environ.get("COVALENT_EXTRA_HEADERS")
        if data:
            return json.loads(data)
        else:
            return {}
