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

"""Transportable object module."""

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
    """Archived transportable object."""

    def __init__(self, header: bytes, object_string: bytes, data: bytes):
        """Initialize TOArchive.

        Args:
            header: Archived transportable object header.
            object_string: Archived transportable object string.
            data: Archived transportable object data.

        """
        self.header = header
        self.object_string = object_string
        self.data = data

    def cat(self) -> bytes:
        """Concatenate TOArchive.

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

    def load(self, header_only: bool, string_only: bool) -> "_TOArchive":
        """Load TOArchive object.

        Args:
            header_only: Load header only.
            string_only: Load string only.

        Returns:
            Archived transportable object.

        """
        string_offset = _TOArchiveUtils.string_offset(self)
        header = _TOArchiveUtils.parse_header(self, string_offset)
        object_string = b""
        data = b""

        if not header_only:
            data_offset = _TOArchiveUtils.data_offset(self)
            object_string = _TOArchiveUtils.parse_string(self, string_offset, data_offset)

            if not string_only:
                data = _TOArchiveUtils.parse_data(self, data_offset)
        return _TOArchive(header, object_string, data)

    def _to_transportable_object(self) -> "TransportableObject":
        """Convert a _TOArchive to a TransportableObject.

        Args:
            ar: Archived transportable object to be converted.

        Returns:
            Transportable object.

        """
        decoded_object_str = self.object_string.decode("utf-8")
        decoded_data = self.data.decode("utf-8")
        decoded_header = json.loads(self.header.decode("utf-8"))
        to = TransportableObject(None)
        to._header = decoded_header
        to._object_string = decoded_object_str or ""
        to._object = decoded_data or ""
        return to


class _TOArchiveUtils:
    """TOArchive utilities object."""

    @staticmethod
    def data_offset(serialized: bytes) -> int:
        """Get data offset.

        Args:
            serialized: Serialized TOArchive.

        Returns:
            Data offset.

        """
        size64 = serialized[STRING_OFFSET_BYTES : STRING_OFFSET_BYTES + DATA_OFFSET_BYTES]
        return int.from_bytes(size64, BYTE_ORDER, signed=False)

    @staticmethod
    def string_offset(serialized: bytes) -> int:
        """String offset.

        Args:
            serialized: Serialized TOArchive.

        Returns:
            String offset.

        """
        size64 = serialized[:STRING_OFFSET_BYTES]
        return int.from_bytes(size64, BYTE_ORDER, signed=False)

    @staticmethod
    def parse_header(serialized: bytes, string_offset: int) -> bytes:
        """Parse TOArchive header.

        Args:
            serialized: Serialized TOArchive.
            string_offset: String offset.

        Returns:
            Serialized TOArchive header.

        """
        return serialized[HEADER_OFFSET:string_offset]

    @staticmethod
    def parse_string(serialized: bytes, string_offset: int, data_offset: int) -> bytes:
        """Parse string.

        Args:
            serialized: Serialized TOArchive.
            string_offset: String offset.
            data_offset: Data offset.

        Returns:
            Serialized TOArchive object string.

        """
        return serialized[string_offset:data_offset]

    @staticmethod
    def parse_data(serialized: bytes, data_offset: int) -> bytes:
        """Parse data.

        Args:
            serialized: Serialized TOArchive.
            data_offset: Data offset.

        Returns:
            Serialized TOArchive data.

        """
        return serialized[data_offset:]


class TransportableObject:
    """
    A function is converted to a transportable object by serializing it using cloudpickle
    and then whenever executing it, the transportable object is deserialized. The object
    will also contain additional info like the python version used to serialize it.
    """

    def __init__(self, obj: Any) -> None:
        """Initialize TransportableObject.

        Args:
            obj: Object to be serialized.

        Attributes:
            _object: The serialized object.
            _object_string: The string representation of the object.
            _header: The header of the object with python version (python version used on the client's machine), doc (Object doc string) and name attributes.

        Returns:
            None

        """
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
        # For version compatibility with older Covalent
        try:
            return self._object_string
        except AttributeError:
            return self.__dict__["object_string"]

    def __eq__(self, obj) -> bool:
        return self.__dict__ == obj.__dict__ if isinstance(obj, TransportableObject) else False

    def get_deserialized(self) -> Callable:
        """
        Get the deserialized transportable object.

        Note that this method is different from the `deserialize` method which deserializes from the `archived` transportable object.

        Returns:
            function: The deserialized object/callable function.

        """
        return cloudpickle.loads(base64.b64decode(self._object.encode("utf-8")))

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self.

        Returns:
            dict: A JSON-serializable dictionary representation of self.

        """
        return {"type": "TransportableObject", "attributes": self.__dict__.copy()}

    @staticmethod
    def from_dict(object_dict) -> "TransportableObject":
        """Rehydrate a dictionary representation.

        Args:
            object_dict: a dictionary representation returned by `to_dict`.

        Returns:
            A `TransportableObject` represented by `object_dict`.

        """
        sc = TransportableObject(None)
        sc.__dict__ = object_dict["attributes"]
        return sc

    def get_serialized(self) -> str:
        """
        Get the serialized transportable object.

        Note that this is different from the `serialize` method which serializes the `archived` transportable object.

        Returns:
            object: The serialized transportable object.

        """
        return self._object

    def serialize(self) -> bytes:
        """
        Serialize the transportable object to the archived transportable object.

        Returns:
            The serialized object along with the python version.

        """
        return self._to_archive().cat()

    def serialize_to_json(self) -> str:
        """
        Serialize the transportable object to JSON.

        Returns:
            A JSON string representation of the transportable object.

        """
        return json.dumps(self.to_dict())

    @staticmethod
    def deserialize_from_json(json_string: str) -> str:
        """
        Reconstruct a transportable object from JSON

        Args:
            json_string: A JSON string representation of a TransportableObject.

        Returns:
            A TransportableObject instance.

        """
        object_dict = json.loads(json_string)
        return TransportableObject.from_dict(object_dict)

    @staticmethod
    def make_transportable(obj: Any) -> "TransportableObject":
        """Make an object transportable.

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
        """Deserialize the transportable object from the archived transportable object.

        Args:
            data: Serialized transportable object

        Returns:
            The deserialized transportable object.

        """
        ar = _TOArchive.load(serialized, header_only, string_only)
        return ar._to_transportable_object()

    @staticmethod
    def deserialize_list(collection: list) -> list:
        """
        Recursively deserializes a list of TransportableObjects. More
        precisely, `collection` is a list, each of whose entries is
        assumed to be either a `TransportableObject`, a list, or dict`

        Args:
            collection: A list of TransportableObjects.

        Returns:
            A list of deserialized objects.

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

    def _to_archive(self) -> _TOArchive:
        """Convert a TransportableObject to a _TOArchive.

        Args:
            to: Transportable object to be converted.

        Returns:
            Archived transportable object.

        """
        header = json.dumps(self._header).encode("utf-8")
        object_string = self._object_string.encode("utf-8")
        data = self._object.encode("utf-8")
        return _TOArchive(header=header, object_string=object_string, data=data)
