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

from ..._shared_files.utils import cloudpickle_deserialize, cloudpickle_serialize
from ..qserver import LocalQServer
from .base_client import BaseQClient

# Since in the local case, the server and client are the same
# thus the "server" class's functions are directly accessed


class LocalQClient(BaseQClient):
    def __init__(self) -> None:
        self.qserver = LocalQServer()

    @property
    def selector(self):
        return self.deserialize(self.qserver.selector)

    @selector.setter
    def selector(self, selector_func):
        self.qserver.selector = self.serialize(selector_func)

    @property
    def database(self):
        return self.deserialize(self.qserver.database)

    def submit(self, qscripts, executors, qelectron_info, qnode_specs):
        ser_qscripts = self.serialize(qscripts)
        ser_executors = self.serialize(executors)
        ser_qelectron_info = self.serialize(qelectron_info)
        ser_qnode_specs = self.serialize(qnode_specs)

        return self.qserver.submit(
            ser_qscripts, ser_executors, ser_qelectron_info, ser_qnode_specs
        )

    def get_results(self, batch_id):
        ser_results = self.qserver.get_results(batch_id)
        return self.deserialize(ser_results)

    def serialize(self, obj):
        return cloudpickle_serialize(obj)

    def deserialize(self, ser_obj):
        return cloudpickle_deserialize(ser_obj)
