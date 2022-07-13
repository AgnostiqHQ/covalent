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

import glob
import os
import pathlib
from enum import Enum

import cloudpickle as pickle

from covalent_ui.app.api_v0.models.file_model import FileExtension, Filetype


def read_from_pickle(path):
    with open(path, "rb") as file:
        try:
            while True:
                yield pickle.load(file)
        except EOFError:
            pass


class FileHandler:
    """File read"""

    def __init__(self, path, file_name) -> None:
        self.path = path
        self.file_name = file_name
        self.file_path = self.path + self.file_name

    def file_read(executor_file_path, file_module):
        executors = {}
        file_extension = pathlib.Path(executor_file_path + file_module).suffix
        if file_extension == FileExtension.PKL.value and file_module != Filetype.EXECUTOR.value:
            for item in read_from_pickle(executor_file_path + file_module):
                vars1 = vars(item)
                for value in vars1:
                    executors[value] = getattr(item, value)
                return executors
            return executors
        elif file_extension == FileExtension.PKL.value and file_module == Filetype.EXECUTOR.value:
            with open(executor_file_path + file_module, "rb") as file:
                data = pickle.load(file)
            return data
        with open(executor_file_path + file_module, "rb") as fd:
            fd.seek(0)
            result = fd.read().decode("utf-8")
            return result
