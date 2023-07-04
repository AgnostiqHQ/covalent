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
