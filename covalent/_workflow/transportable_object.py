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

#  [string offset (8 bytes), big][data offset (8 bytes), big][header][string][data]

STRING_OFFSET_BYTES = 8
DATA_OFFSET_BYTES = 8
HEADER_OFFSET = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES
BYTE_ORDER = "big"


class _TOArchive:
    def __init__(self, header: bytes, object_string: bytes, data: bytes):
        self.header = header
        self.object_string = object_string
        self.data = data

    def cat(self) -> bytes:
        header_size = len(self.header)
        string_size = len(self.object_string)
        data_offset = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES + header_size + string_size
        string_offset = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES + header_size

        data_offset = data_offset.to_bytes(DATA_OFFSET_BYTES, BYTE_ORDER, signed=False)
        string_offset = string_offset.to_bytes(STRING_OFFSET_BYTES, BYTE_ORDER, signed=False)

        return string_offset + data_offset + self.header + self.object_string + self.data

    def load(serialized: bytes, header_only: bool, string_only: bool) -> "_TOArchive":
        string_offset = _TOArchiveUtils.string_offset(serialized)
        header = _TOArchiveUtils.parse_header(serialized, string_offset)
        object_string = b""
        data = b""

        if not header_only:
            data_offset = _TOArchiveUtils.data_offset(serialized)
            object_string = _TOArchiveUtils.parse_string(serialized, string_offset, data_offset)

            if not string_only:
                data = _TOArchiveUtils.parse_data(serialized, data_offset)
        return _TOArchive(header, object_string, data)


class _TOArchiveUtils:
    @staticmethod
    def data_offset(serialized: bytes) -> int:
        size64 = serialized[STRING_OFFSET_BYTES : STRING_OFFSET_BYTES + DATA_OFFSET_BYTES]
        return int.from_bytes(size64, BYTE_ORDER, signed=False)

    @staticmethod
    def string_offset(serialized: bytes) -> int:
        size64 = serialized[:STRING_OFFSET_BYTES]
        return int.from_bytes(size64, BYTE_ORDER, signed=False)

    @staticmethod
    def parse_header(serialized: bytes, string_offset: int) -> bytes:
        header = serialized[HEADER_OFFSET:string_offset]
        return header

    @staticmethod
    def parse_string(serialized: bytes, string_offset: int, data_offset: int) -> bytes:
        return serialized[string_offset:data_offset]

    @staticmethod
    def parse_data(serialized: bytes, data_offset: int) -> bytes:
        return serialized[data_offset:]


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
        b64object = base64.b64encode(cloudpickle.dumps(obj))
        object_string_u8 = str(obj).encode("utf-8")

        self._object = b64object.decode("utf-8")
        self._object_string = object_string_u8.decode("utf-8")

        self._header = {
            "py_version": platform.python_version(),
            "attrs": {
                "doc": getattr(obj, "__doc__", ""),
                "name": getattr(obj, "__name__", ""),
            },
        }

    @property
    def python_version(self):
        return self._header["py_version"]

    @property
    def attrs(self):
        return self._header["attrs"]

    @property
    def object_string(self):
        return self._object_string

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

        return _to_archive(self).cat()

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
    def deserialize(
        serialized: bytes, *, header_only: bool = False, string_only: bool = False
    ) -> "TransportableObject":
        """
        Deserialize the transportable object.

        Args:
            data: serialized transportable object

        Returns:
            object: The deserialized transportable object.
        """

        ar = _TOArchive.load(serialized, header_only, string_only)
        return _from_archive(ar)

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


def _to_archive(to: TransportableObject) -> _TOArchive:
    header = json.dumps(to._header).encode("utf-8")
    object_string = to._object_string.encode("utf-8")
    data = to._object.encode("utf-8")
    return _TOArchive(header=header, object_string=object_string, data=data)


def _from_archive(ar: _TOArchive) -> TransportableObject:
    decoded_object_str = ar.object_string.decode("utf-8")
    decoded_data = ar.data.decode("utf-8")
    decoded_header = json.loads(ar.header.decode("utf-8"))
    to = TransportableObject(None)
    to._header = decoded_header
    to._object_string = decoded_object_str if decoded_object_str else ""
    to._object = decoded_data if decoded_data else ""

    return to
