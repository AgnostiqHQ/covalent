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
from typing import Callable, Union

from ..._shared_files.utils import cloudpickle_deserialize, cloudpickle_serialize
from .base import AsyncBaseQCluster, BaseQExecutor
from .default_selectors import selector_map

__all__ = [
    "QCluster",
]


class QCluster(AsyncBaseQCluster):
    """
    A cluster of quantum executors.

    Args:
        executors: A sequence of quantum executors.
        selector: A callable that selects an executor, or one of the strings "cyclic"
            or "random". The "cyclic" selector (default) cycles through `executors`
            and returns the next executor for each circuit. The "random" selector
            chooses an executor from `executors` at random for each circuit. Any
            user-defined selector must be callable with two positional arguments,
            a circuit and a list of executors. A selector must also return exactly
            one executor.
    """

    selector: Union[str, Callable] = "cyclic"

    # Flag used to indicate whether `self.selector` is currently serialized.
    # This needs to be without the "_" prefix so that it gets propagated to the server.
    selector_serialized: bool = False

    def batch_submit(self, qscripts_list):
        if self.selector_serialized:
            self.selector = self.deserialize_selector()

        selector = self.get_selector()
        selected_executor: BaseQExecutor = selector(qscripts_list, self.executors)

        # Copy server-side set attributes into selector executor.
        selected_executor.qelectron_info = self.qelectron_info.copy()
        return selected_executor.batch_submit(qscripts_list)

    def serialize_selector(self) -> None:
        if self.selector_serialized:
            return

        # serialize to bytes with cloudpickle
        self.selector = cloudpickle_serialize(self.selector)

        # convert to string to make JSON-able
        self.selector = base64.b64encode(self.selector).decode("utf-8")
        self.selector_serialized = True

    def deserialize_selector(self) -> Union[str, Callable]:
        if not self.selector_serialized:
            return self.selector

        # Deserialize the selector function (or string).
        selector = cloudpickle_deserialize(base64.b64decode(self.selector.encode("utf-8")))

        self.selector_serialized = False
        return selector

    def dict(self, *args, **kwargs) -> dict:
        # override `dict` method to convert dict attributes to JSON strings
        dict_ = super(AsyncBaseQCluster, self).dict(*args, **kwargs)
        dict_.update(executors=tuple(ex.json() for ex in self.executors))
        return dict_

    def get_selector(self) -> Callable:
        """
        Wraps `self.selector` to return defaults corresponding to string values.

        This method is called inside `batch_submit`.
        """
        self.selector = self.deserialize_selector()

        if isinstance(self.selector, str):
            # use default selector
            selector_cls = selector_map[self.selector]
            self.selector = selector_cls()

        return self.selector
