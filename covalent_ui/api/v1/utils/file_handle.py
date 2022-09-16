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

import json

import cloudpickle as pickle

from covalent._workflow.transport import TransportableObject, _TransportGraph


def validate_data(unpickled_object):
    """Validate unpickled object"""
    if isinstance(unpickled_object, list):
        if not (unpickled_object):
            return ""
        else:
            list_str = ""
            for obj in unpickled_object:
                list_str += obj
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

            return json.dumps({"args": args_array, "kwargs": kwargs_array})
        else:
            return None
    elif isinstance(unpickled_object, str):
        return (
            unpickled_object if (unpickled_object != "" or unpickled_object is not None) else None
        )
    elif isinstance(unpickled_object, TransportableObject):
        res = unpickled_object.object_string
        return json.dumps(res)
    elif isinstance(unpickled_object, _TransportGraph):
        return str(unpickled_object.__dict__)
    else:
        return unpickled_object


class FileHandler:
    """File read"""

    def __init__(self, location) -> None:
        self.location = location

    def read_from_pickle(self, path):
        """Return data from pickle file"""
        try:
            unpickled_object = self.__unpickle_file(path)
            return validate_data(unpickled_object)
        except Exception:
            return None

    def read_from_text(self, path):
        """Return data from text file"""
        try:
            with open(self.location + "/" + path, "r", encoding="utf-8") as read_file:
                text_object = read_file.readlines()
                list_str = ""
                read_file.close()
                if isinstance(text_object, list):
                    for i in text_object:
                        list_str += i
                    return list_str if (list_str != "" or list_str is not None) else None
                else:
                    return text_object if (text_object != "" or text_object is not None) else None
        except EOFError:
            return None
        except Exception:
            return None

    def __unpickle_file(self, path):
        try:
            with open(self.location + "/" + path, "rb") as read_file:
                unpickled_object = pickle.load(read_file)
                read_file.close()
                return unpickled_object
        except EOFError:
            return None
