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
