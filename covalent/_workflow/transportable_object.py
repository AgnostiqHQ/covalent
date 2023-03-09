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

"""TransportableObject"""

import base64
import json
import platform
from typing import Any, Callable

import cloudpickle


class TransportableObject:
    """
    A function is converted to a transportable object by serializing it using cloudpickle
    and then whenever executing it, the transportable object is deserialized. The object
    will also contain additional info like the python version used to serialize it.

    Attributes:
        _object: The serialized object.
        python_version: The python version used on the client's machine.
    """

    def __init__(self, obj: Any) -> None:
        self._object = base64.b64encode(cloudpickle.dumps(obj)).decode("utf-8")
        self.python_version = platform.python_version()

        self.object_string = str(obj)
        self.attrs = {"doc": getattr(obj, "__doc__", ""), "name": getattr(obj, "__name__", "")}

    def __eq__(self, obj) -> bool:
        if not isinstance(obj, TransportableObject):
            return False
        return self.__dict__ == obj.__dict__

    def get_deserialized(self) -> Callable:
        """
        Get the deserialized transportable object.

        Args:
            None

        Returns:
            function: The deserialized object/callable function.

        """

        return cloudpickle.loads(base64.b64decode(self._object.encode("utf-8")))

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        return {"type": "TransportableObject", "attributes": self.__dict__.copy()}

    @staticmethod
    def from_dict(object_dict) -> "TransportableObject":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            A `TransportableObject` represented by `object_dict`
        """

        sc = TransportableObject(None)
        sc.__dict__ = object_dict["attributes"]
        return sc

    def get_serialized(self) -> str:
        """
        Get the serialized transportable object.

        Args:
            None

        Returns:
            object: The serialized transportable object.
        """

        return self._object

    def serialize(self) -> bytes:
        """
        Serialize the transportable object.

        Args:
            None

        Returns:
            pickled_object: The serialized object alongwith the python version.
        """

        return cloudpickle.dumps(
            {
                "object": self.get_serialized(),
                "object_string": self.object_string,
                "attrs": self.attrs,
                "py_version": self.python_version,
            }
        )

    def serialize_to_json(self) -> str:
        """
        Serialize the transportable object to JSON.

        Args:
            None

        Returns:
            A JSON string representation of the transportable object
        """

        return json.dumps(self.to_dict())

    @staticmethod
    def deserialize_from_json(json_string: str) -> str:
        """
        Reconstruct a transportable object from JSON

        Args:
            json_string: A JSON string representation of a TransportableObject

        Returns:
            A TransportableObject instance
        """

        object_dict = json.loads(json_string)
        return TransportableObject.from_dict(object_dict)

    @staticmethod
    def make_transportable(obj) -> "TransportableObject":
        if isinstance(obj, TransportableObject):
            return obj
        else:
            return TransportableObject(obj)

    @staticmethod
    def deserialize(data: bytes) -> "TransportableObject":
        """
        Deserialize the transportable object.

        Args:
            data: Cloudpickled function.

        Returns:
            object: The deserialized transportable object.
        """

        obj = cloudpickle.loads(data)
        sc = TransportableObject(None)
        sc._object = obj["object"]
        sc.attrs = obj["attrs"]
        sc.python_version = obj["py_version"]
        return sc

    @staticmethod
    def deserialize_list(collection: list) -> list:
        """
        Recursively deserializes a list of TransportableObjects. More
        precisely, `collection` is a list, each of whose entries is
        assumed to be either a `TransportableObject`, a list, or dict`
        """

        new_list = []
        for item in collection:
            if isinstance(item, TransportableObject):
                new_list.append(item.get_deserialized())
            elif isinstance(item, list):
                new_list.append(TransportableObject.deserialize_list(item))
            elif isinstance(item, dict):
                new_list.append(TransportableObject.deserialize_dict(item))
            else:
                raise TypeError("Couldn't deserialize collection")
        return new_list

    @staticmethod
    def deserialize_dict(collection: dict) -> dict:
        """
        Recursively deserializes a dict of TransportableObjects. More
        precisely, `collection` is a dict, each of whose entries is
        assumed to be either a `TransportableObject`, a list, or dict`

        """

        new_dict = {}
        for k, item in collection.items():
            if isinstance(item, TransportableObject):
                new_dict[k] = item.get_deserialized()
            elif isinstance(item, list):
                new_dict[k] = TransportableObject.deserialize_list(item)
            elif isinstance(item, dict):
                new_dict[k] = TransportableObject.deserialize_dict(item)
            else:
                raise TypeError("Couldn't deserialize collection")
        return new_dict
