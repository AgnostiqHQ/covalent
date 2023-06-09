import base64

import orjson

from ..executors.base import AsyncBaseQCluster
from ..shared_utils import cloudpickle_deserialize, cloudpickle_serialize

__all__ = [
    "QCluster",
]


class QCluster(AsyncBaseQCluster):

    _selector_serialized: bool = False

    def batch_submit(self, qscripts):
        if self._selector_serialized:
            self.deserialize_selector()

        selected_executor = self.selector(qscripts, self.executors)
        return selected_executor.batch_submit(qscripts)

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
