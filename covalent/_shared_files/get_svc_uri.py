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

import os

from furl import furl


class ServiceURI:
    def __init__(
        self,
        scheme: str = "http",
        host: str = "localhost",
        port: int = None,
        prefix: str = "api/v0",
    ) -> None:
        self.scheme = scheme
        self.host = host
        self.port = port
        self.prefix = prefix

    def get_base_url(self):
        base_url = furl().set(scheme=self.scheme, host=self.host, port=self.port)
        if self.prefix:
            base_url.set(path=self.prefix)
        return base_url

    def get_route(self, path: str):
        base_url = self.get_base_url().copy()
        base_url.path /= path
        return base_url.url


class DispatcherURI(ServiceURI):
    def __init__(self) -> None:
        super().__init__(
            port=os.getenv("DISPATCHER_SVC_PORT", 8002),
            host=os.getenv("DISPATCHER_SVC_HOST", "localhost"),
        )


class QueuerURI(ServiceURI):
    def __init__(self) -> None:
        super().__init__(
            port=os.getenv("QUEUER_SVC_PORT", 8001), host=os.getenv("QUEUER_SVC_HOST", "localhost")
        )


class ResultsURI(ServiceURI):
    def __init__(self) -> None:
        super().__init__(
            port=os.getenv("RESULTS_SVC_PORT", 8006),
            host=os.getenv("RESULTS_SVC_HOST", "localhost"),
        )
