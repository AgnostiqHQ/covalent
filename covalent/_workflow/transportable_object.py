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
from typing import Any, Callable, Dict, Tuple

import cloudpickle

#  [string offset (8 bytes), big][data offset (8 bytes), big][header][string][data]

STRING_OFFSET_BYTES = 8
DATA_OFFSET_BYTES = 8
HEADER_OFFSET = STRING_OFFSET_BYTES + DATA_OFFSET_BYTES
BYTE_ORDER = "big"
TOBJ_FMT_STR = "0.1"


class TOArchiveUtils:
    """Utilities for reading serialized TransportableObjects"""

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
        """Return byte range for the picklebytes"""
        start_byte = TOArchiveUtils.data_offset(serialized)
        return start_byte, -1

    @staticmethod
    def header(serialized: bytes) -> dict:
        string_offset = TOArchiveUtils.string_offset(serialized)
        header = serialized[HEADER_OFFSET:string_offset]
        return json.loads(header.decode("utf-8"))

    @staticmethod
    def string_segment(serialized: bytes) -> bytes:
        string_offset = TOArchiveUtils.string_offset(serialized)
        data_offset = TOArchiveUtils.data_offset(serialized)
        return serialized[string_offset:data_offset]

    @staticmethod
    def data_segment(serialized: bytes) -> bytes:
        data_offset = TOArchiveUtils.data_offset(serialized)
        return serialized[data_offset:]


class _ByteArrayFile:
    """File-like interface for appending to a bytearray."""

    def __init__(self, buf: bytearray):
        self._buf = buf

    def write(self, data: bytes):
        self._buf.extend(data)


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
        self._buffer = bytearray()

        # Reserve space for the byte offsets to be written at the end
        self._buffer.extend(b"\0" * HEADER_OFFSET)

        _header = {
            "format": TOBJ_FMT_STR,
            "py_version": platform.python_version(),
            "cloudpickle_version": cloudpickle.__version__,
            "attrs": {
                "doc": getattr(obj, "__doc__", ""),
                "name": getattr(obj, "__name__", ""),
            },
        }

        # Write header and object string
        header_u8 = json.dumps(_header).encode("utf-8")
        header_len = len(header_u8)

        object_string_u8 = str(obj).encode("utf-8")
        object_string_len = len(object_string_u8)

        self._buffer.extend(header_u8)
        self._buffer.extend(object_string_u8)
        del object_string_u8

        # Append picklebytes (not base64-encoded)
        cloudpickle.dump(obj, _ByteArrayFile(self._buffer))

        # Write byte offsets
        string_offset = HEADER_OFFSET + header_len
        data_offset = string_offset + object_string_len

        string_offset_bytes = string_offset.to_bytes(STRING_OFFSET_BYTES, BYTE_ORDER)
        data_offset_bytes = data_offset.to_bytes(DATA_OFFSET_BYTES, BYTE_ORDER)
        self._buffer[:STRING_OFFSET_BYTES] = string_offset_bytes
        self._buffer[STRING_OFFSET_BYTES:HEADER_OFFSET] = data_offset_bytes

    @property
    def python_version(self):
        return self.header["py_version"]

    @property
    def header(self):
        return TOArchiveUtils.header(self._buffer)

    @property
    def attrs(self):
        return self.header["attrs"]

    @property
    def object_string(self):
        # For compatibility with older Covalent
        try:
            return (
                TOArchiveUtils.string_segment(memoryview(self._buffer)).tobytes().decode("utf-8")
            )
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

        return cloudpickle.loads(TOArchiveUtils.data_segment(memoryview(self._buffer)))

    def to_dict(self) -> dict:
        """Return a JSON-serializable dictionary representation of self"""
        attr_dict = {
            "buffer_b64": base64.b64encode(memoryview(self._buffer)).decode("utf-8"),
        }

        return {"type": "TransportableObject", "attributes": attr_dict}

    @staticmethod
    def from_dict(object_dict) -> "TransportableObject":
        """Rehydrate a dictionary representation

        Args:
            object_dict: a dictionary representation returned by `to_dict`

        Returns:
            A `TransportableObject` represented by `object_dict`
        """

        sc = TransportableObject(None)
        sc._buffer = base64.b64decode(object_dict["attributes"]["buffer_b64"].encode("utf-8"))
        return sc

    def get_serialized(self) -> str:
        """
        Get the serialized transportable object.

        Args:
            None

        Returns:
            object: The serialized transportable object.
        """

        # For backward compatibility
        data_segment = TOArchiveUtils.data_segment(memoryview(self._buffer))
        return base64.b64encode(data_segment).decode("utf-8")

    def serialize(self) -> bytes:
        """
        Serialize the transportable object.

        Args:
            None

        Returns:
            pickled_object: The serialized object alongwith the python version.
        """

        return self._buffer

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
    def deserialize(serialized: bytes) -> "TransportableObject":
        """
        Deserialize the transportable object.

        Args:
            data: serialized transportable object

        Returns:
            object: The deserialized transportable object.
        """
        to = TransportableObject(None)
        header = TOArchiveUtils.header(serialized)

        # For backward compatibility
        if header.get("format") is None:
            # Re-encode TObj serialized using older versions of the SDK,
            # characterized by the lack of a "format" field in the
            # header. TObj was previously serialized as
            # [offsets][header][string][b64-encoded picklebytes],
            # whereas starting from format 0.1 we store them as
            # [offsets][header][string][picklebytes].
            to._buffer = TransportableObject._upgrade_tobj_format(serialized, header)
        else:
            to._buffer = serialized
        return to

    @staticmethod
    def _upgrade_tobj_format(serialized: bytes, header: Dict) -> bytes:
        """Re-encode a serialized TObj in the newer format.

        This involves adding a format version in the header and
        base64-decoding the data segment. Because the header at the
        beginning of the byte array, the string and data offsets need
        to be recomputed.
        """
        buf = bytearray()

        # Upgrade header and recompute byte offsets
        header["format"] = TOBJ_FMT_STR
        serialized_header = json.dumps(header).encode("utf-8")
        string_offset = HEADER_OFFSET + len(serialized_header)

        # This is just a view into the bytearray and consumes
        # negligible space on its own.
        string_segment = TOArchiveUtils.string_segment(serialized)

        data_offset = string_offset + len(string_segment)
        string_offset_bytes = string_offset.to_bytes(STRING_OFFSET_BYTES, BYTE_ORDER)
        data_offset_bytes = data_offset.to_bytes(DATA_OFFSET_BYTES, BYTE_ORDER)

        # Write the new byte offsets
        buf.extend(b"\0" * HEADER_OFFSET)
        buf[:STRING_OFFSET_BYTES] = string_offset_bytes
        buf[STRING_OFFSET_BYTES:HEADER_OFFSET] = data_offset_bytes

        buf.extend(serialized_header)
        buf.extend(string_segment)

        # base64-decode the data segment into raw picklebytes
        buf.extend(base64.b64decode(TOArchiveUtils.data_segment(serialized)))

        return buf

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
