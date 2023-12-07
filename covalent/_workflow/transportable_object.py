# Copyright 2021 Agnostiq Inc.
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

"""Transportable object module defining relevant classes and functions"""

import base64
import json
import platform
from typing import Any, Callable, Tuple

import cloudpickle

#  [string offset (8 bytes), big][data offset (8 bytes), big][header][string][data]

STRING_OFFSET_BYTES = 8
DATA_OFFSET_BYTES = 8
HEADER_OFFSET = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES
BYTE_ORDER = "big"


class _TOArchive:

    """Archived transportable object."""

    def __init__(self, header: bytes, object_string: bytes, data: bytes):
        """
        Initialize TOArchive.

        Args:
            header: Archived transportable object header.
            object_string: Archived transportable object string.
            data: Archived transportable object data.

        Returns:
            None
        """

        self.header = header
        self.object_string = object_string
        self.data = data

    def cat(self) -> bytes:
        """
        Concatenate TOArchive.

        Returns:
            Concatenated TOArchive.

        """

        header_size = len(self.header)
        string_size = len(self.object_string)
        data_offset = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES + header_size + string_size
        string_offset = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES + header_size

        data_offset = data_offset.to_bytes(DATA_OFFSET_BYTES, BYTE_ORDER, signed=False)
        string_offset = string_offset.to_bytes(STRING_OFFSET_BYTES, BYTE_ORDER, signed=False)

        return string_offset + data_offset + self.header + self.object_string + self.data

    @staticmethod
    def load(serialized: bytes, header_only: bool, string_only: bool) -> "_TOArchive":
        """
        Load TOArchive object from serialized bytes.

        Args:
            serialized: Serialized transportable object.
            header_only: Load header only.
            string_only: Load string only.

        Returns:
            Archived transportable object.

        """

        string_offset = TOArchiveUtils.string_offset(serialized)
        header = TOArchiveUtils.parse_header(serialized, string_offset)
        object_string = b""
        data = b""

        if not header_only:
            data_offset = TOArchiveUtils.data_offset(serialized)
            object_string = TOArchiveUtils.parse_string(serialized, string_offset, data_offset)

            if not string_only:
                data = TOArchiveUtils.parse_data(serialized, data_offset)
        return _TOArchive(header, object_string, data)


class TOArchiveUtils:
    @staticmethod
    def data_offset(serialized: bytes) -> int:
        size64 = serialized[STRING_OFFSET_BYTES : STRING_OFFSET_BYTES + DATA_OFFSET_BYTES]
        return int.from_bytes(size64, BYTE_ORDER, signed=False)

    @staticmethod
    def string_offset(serialized: bytes) -> int:
        size64 = serialized[:STRING_OFFSET_BYTES]
        return int.from_bytes(size64, BYTE_ORDER, signed=False)

    @staticmethod
    def string_byte_range(serialized: bytes) -> Tuple[int, int]:
        """Return byte range for the string representation"""
        start_byte = TOArchiveUtils.string_offset(serialized)
        end_byte = TOArchiveUtils.data_offset(serialized)
        return start_byte, end_byte

    @staticmethod
    def data_byte_range(serialized: bytes) -> Tuple[int, int]:
        """Return byte range for the b64 picklebytes"""
        start_byte = TOArchiveUtils.data_offset(serialized)
        return start_byte, -1

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
            "cloudpickle_version": cloudpickle.__version__,
            "attrs": {
                "doc": getattr(obj, "__doc__", ""),
                "name": getattr(obj, "__name__", ""),
            },
        }

    @property
    def python_version(self):
        return self._header["py_version"]

    @property
    def header(self):
        return self._header

    @property
    def attrs(self):
        return self._header["attrs"]

    @property
    def object_string(self):
        # For compatibility with older Covalent
        try:
            return self._object_string
        except AttributeError:
            return self.__dict__["object_string"]

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
        """
        Make an object transportable.

        Args:
            obj: The object to make transportable.

        Returns:
            Transportable object.

        """

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

        Args:
            collection: A dictionary of TransportableObjects.
        Returns:
            A dictionary of deserialized objects.

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
    """
    Convert a TransportableObject to a _TOArchive.

    Args:
        to: Transportable object to be converted.

    Returns:
        Archived transportable object.

    """

    header = json.dumps(to._header).encode("utf-8")
    object_string = to._object_string.encode("utf-8")
    data = to._object.encode("utf-8")
    return _TOArchive(header=header, object_string=object_string, data=data)


def _from_archive(ar: _TOArchive) -> TransportableObject:
    """
    Convert a _TOArchive to a TransportableObject.

    Args:
        ar: Archived transportable object.

    Returns:
        Transportable object.

    """

    decoded_object_str = ar.object_string.decode("utf-8")
    decoded_data = ar.data.decode("utf-8")
    decoded_header = json.loads(ar.header.decode("utf-8"))
    to = TransportableObject(None)
    to._header = decoded_header
    to._object_string = decoded_object_str or ""
    to._object = decoded_data or ""

    return to
