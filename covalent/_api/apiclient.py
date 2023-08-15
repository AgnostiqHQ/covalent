# Copyright 2023 Agnostiq Inc.
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
