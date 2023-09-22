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

import asyncio
from abc import ABC, abstractmethod
from concurrent.futures import Future
from typing import Callable, List, Sequence, Union

from mpire.async_result import AsyncResult
from pydantic import BaseModel, Extra

from ...executor.qbase import AsyncBaseQExecutor, BaseQExecutor, QCResult


class AsyncBaseQCluster(AsyncBaseQExecutor):
    executors: Sequence[BaseQExecutor]
    selector: Union[str, Callable]

    # Flag used to indicate whether `self.selector` is currently serialized.
    # This needs to be without the "_" prefix so that it gets propagated to the server.
    selector_serialized: bool = False

    @abstractmethod
    def serialize_selector(self) -> None:
        """
        Serializes the cluster's selector function.
        """
        raise NotImplementedError

    @abstractmethod
    def deserialize_selector(self) -> Union[str, Callable]:
        """
        Deserializes the cluster's selector function.
        """
        raise NotImplementedError

    @abstractmethod
    def dict(self, *args, **kwargs) -> dict:
        """
        Custom dict method to create a hashable `executors` attribute.
        """
        raise NotImplementedError

    @abstractmethod
    def get_selector(self):
        """
        Returns the deserialized selector function.
        """
        raise NotImplementedError

    async def _get_result(self, futures_list: List) -> List[QCResult]:
        """
        Override the base method to handle the case where the `futures_list`
        contains a mix of object types from various executors.
        """
        results_and_times = []
        for fut in futures_list:
            if isinstance(fut, asyncio.Task):
                results_and_times.append(await fut)
            elif isinstance(fut, Future):
                results_and_times.append(fut.result())
            elif isinstance(fut, AsyncResult):
                results_and_times.append(fut.get())
            else:
                results_and_times.append(fut)

        return results_and_times


class BaseQSelector(ABC, BaseModel):
    name: str = "base_qselector"

    def __call__(self, qscript, executors):
        """ "
        Interface used by the quantum server.
        """
        return self.selector_function(qscript, executors)

    @abstractmethod
    def selector_function(self, qscript, executors):
        """
        Implement selection logic here.
        """
        raise NotImplementedError

    class Config:
        # Allows defining extra state fields in subclasses.
        extra = Extra.allow
