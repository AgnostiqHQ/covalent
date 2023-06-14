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

import base64

from ..executors.base import AsyncBaseQCluster
from ..shared_utils import cloudpickle_deserialize, cloudpickle_serialize

__all__ = [
    "QCluster",
]


class QCluster(AsyncBaseQCluster):

    _selector_serialized: bool = False

    def batch_submit(self, qscripts_list):
        if self._selector_serialized:
            self.deserialize_selector()

        selected_executor = self.selector(qscripts_list, self.executors)

        # pylint: disable=protected-access
        selected_executor._device_cls_import_path = self._device_cls_import_path

        return selected_executor.batch_submit(qscripts_list)

    def serialize_selector(self) -> None:
        if self._selector_serialized:
            return

        # serialize to bytes with cloudpickle
        self.selector = cloudpickle_serialize(self.selector)

        # convert to string to make JSON-able
        self.selector = base64.b64encode(self.selector).decode("utf-8")
        self._selector_serialized = True

    def deserialize_selector(self) -> None:
        if not self._selector_serialized:
            return

        # convert JSON-able string back to bytes
        self.selector = base64.b64decode(self.selector.encode("utf-8"))

        # deserialize to function
        self.selector = cloudpickle_deserialize(self.selector)
        self._selector_serialized = False

    def dict(self, *args, **kwargs) -> dict:
        # override `dict` method to convert dict attributes to JSON strings
        d = super(AsyncBaseQCluster, self).dict(*args, **kwargs)
        d.update(executors=tuple(ex.json() for ex in self.executors))
        return d
