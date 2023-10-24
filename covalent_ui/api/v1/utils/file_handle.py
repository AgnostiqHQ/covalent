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

"""File handlers"""

import base64
import json

import cloudpickle as pickle

from covalent._workflow.transport import TransportableObject, _TransportGraph
from covalent_dispatcher._dal.asset import local_store


def transportable_object(obj):
    """Decode transportable object
    Args:
        obj: Covalent transportable object
    Returns:
        Decoded transportable object
    """
    if obj:
        load_pickle = base64.b64decode(obj._object.encode("utf-8"))
        return f"\npickle.loads({load_pickle})"
    return None


def validate_data(unpickled_object):
    """Validate unpickled object"""
    if isinstance(unpickled_object, list):
        if not (unpickled_object):
            return ""
        else:
            list_str = "".join([obj for obj in unpickled_object])
            return list_str
    if isinstance(unpickled_object, dict):
        args_array = []
        kwargs_array = {}
        if bool(unpickled_object):
            if "type" in unpickled_object:
                return unpickled_object
            for obj in unpickled_object["args"]:
                args_array.append(obj.object_string) if obj is not None else None

            for obj in unpickled_object["kwargs"]:
                kwargs_array[obj] = (
                    unpickled_object["kwargs"][obj].object_string
                    if unpickled_object["kwargs"][obj] is not None
                    else None
                )

            to_transportable_object = TransportableObject(
                {"args": tuple(args_array), "kwargs": kwargs_array}
            )
            object_bytes = transportable_object(to_transportable_object)
            return (
                str(({"args": tuple(args_array), "kwargs": kwargs_array})),
                f"import pickle{object_bytes}",
            )
        else:
            return None
    elif isinstance(unpickled_object, str):
        return (
            unpickled_object if (unpickled_object != "" or unpickled_object is not None) else None
        )
    elif isinstance(unpickled_object, TransportableObject):
        object_bytes = transportable_object(unpickled_object)
        res = unpickled_object.object_string
        return (
            json.dumps(res),
            f"import pickle{object_bytes}",
        )
    elif isinstance(unpickled_object, _TransportGraph):
        return str(unpickled_object.__dict__)
    else:
        return unpickled_object, unpickled_object


class FileHandler:
    """File read"""

    def __init__(self, location) -> None:
        self.location = location

    def read_from_pickle(self, path):
        """Return data from pickle file"""
        try:
            unpickled_object = self.__unpickle_file(path)
            res = validate_data(unpickled_object)
            return res
        except Exception:
            return None

    def read_from_serialized(self, path):
        """Return data from serialized object"""
        try:
            deserialized_obj = local_store.load_file(self.location, path)
            return validate_data(deserialized_obj)
        except Exception as e:
            return None

    def read_from_text(self, path):
        """Return data from text file"""
        try:
            with open(self.location + "/" + path, "r", encoding="utf-8") as read_file:
                text_object = read_file.read()
                read_file.close()
                return text_object if text_object is not None else ""
        except Exception:
            return None

    def __unpickle_file(self, path):
        try:
            with open(self.location + "/" + path, "rb") as read_file:
                unpickled_object = pickle.load(read_file)
                read_file.close()
                return unpickled_object
        except Exception:
            return None
