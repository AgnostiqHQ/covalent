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

import codecs
import json

import cloudpickle as pickle
import regex as rx

from covalent._workflow.transport import TransportableObject, _TransportGraph


def remove_control_characters(str):
    return rx.sub(r"\p{C}", "", str)


class FileHandler:
    """File read"""

    def __init__(self, location) -> None:
        self.location = location

    def read_from_pickle(self, path):
        try:
            read_file = open(self.location + "/" + path, "rb")
            unpickled_object = pickle.load(read_file)
            read_file.close()
            print(type(unpickled_object))
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
                    for obj in unpickled_object["args"]:
                        args_array.append(obj.object_string)

                    for obj in unpickled_object["kwargs"]:
                        kwargs_array[obj] = unpickled_object["kwargs"][obj].object_string

                    return json.dumps({"args": args_array, "kwargs": kwargs_array})
                else:
                    return ""
            elif isinstance(unpickled_object, str):
                return unpickled_object
            elif isinstance(unpickled_object, TransportableObject):
                res = unpickled_object.object_string
                print(res)
                return json.dumps(res)
            elif isinstance(unpickled_object, _TransportGraph):
                return str(unpickled_object.__dict__)
            else:
                return unpickled_object
        except EOFError:
            pass

    def read_from_text(self, path):
        """Read from text"""
        file = codecs.open(self.location + "/" + path, "rb").read().decode("ISO-8859-1")
        return remove_control_characters(file)
