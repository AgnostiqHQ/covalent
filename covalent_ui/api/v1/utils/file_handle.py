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

"""File handlers"""

import base64
import json

import cloudpickle as pickle

from covalent._workflow.transport import TransportableObject


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


def is_list(unpickled_object):
    """
    Check if the unpickled object is of type list or not
    if its list, convert and return the object as string
    """
    return "".join([obj for obj in unpickled_object]) if unpickled_object else ""


def is_dict(unpickled_object):
    """
    Check if the unpickled object is of type dict or not
    if its dict, convert and return the object as string
    """
    if bool(unpickled_object):
        if "type" in unpickled_object:
            return str(unpickled_object)
        deserialized_dict = TransportableObject.deserialize_dict(unpickled_object)
        to_transportable_object = TransportableObject(deserialized_dict)
        object_bytes = transportable_object(to_transportable_object)
        return (str(deserialized_dict), f"import pickle{object_bytes}")
    return None


def is_transportable_object(unpickled_object):
    """
    Check if the unpickled object is transportable object or not
    if its transportable object, convert and return the object as string
    """
    object_bytes = transportable_object(unpickled_object)
    res = unpickled_object.object_string
    return (
        json.dumps(res),
        f"import pickle{object_bytes}",
    )


def is_transport_graph(unpickled_object):
    """
    Check if the unpickled object is transport graph or not
    if its transport graph, convert and return the object as string
    """
    return str(unpickled_object.__dict__)


def is_str(unpickled_object):
    """
    Check if the unpickled object is string or not
    """
    return unpickled_object


def is_none(_):
    """
    Check if the unpickled object is string or not
    """
    return "None"


types_switch = {
    "list": is_list,
    "dict": is_dict,
    "TransportableObject": is_transportable_object,
    "_TransportGraph": is_transport_graph,
    "str": is_str,
    "NoneType": is_none,
}


def validate_data(unpickled_object):
    """Validate unpickled object"""
    object_type = type(unpickled_object).__name__
    switcher = types_switch.get(object_type, unpickled_object)
    return switcher(unpickled_object)


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
