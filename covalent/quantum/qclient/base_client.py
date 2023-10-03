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

from abc import ABC, abstractmethod, abstractproperty


class BaseQClient(ABC):
    @abstractmethod
    def submit(self, qscripts, executors, qelectron_info, qnode_specs):
        raise NotImplementedError

    @abstractmethod
    def get_results(self, batch_id):
        raise NotImplementedError

    @abstractproperty
    def selector(self):
        raise NotImplementedError

    @abstractproperty
    def database(self):
        raise NotImplementedError

    # The following methods are abstract because the qserver
    # is expecting serialized inputs and will be sending
    # back serialized outputs, thus even if these methods
    # essentially just pass through, for e.g in the LocalQClient's
    # case, they are still to be implemented by the child class and
    # should use the same seriliazing/deserializing method as is being
    # used by the equivalent qserver.
    @abstractmethod
    def serialize(self, obj):
        raise NotImplementedError

    @abstractmethod
    def deserialize(self, ser_obj):
        raise NotImplementedError
