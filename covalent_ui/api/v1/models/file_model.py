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

"""Lattice file module mapper"""

from enum import Enum


class Filetype(str, Enum):
    """Map module for mapping file module to their
    corresponding file extensions"""

    RESULT = "result.pkl"
    OUTPUT = "output"
    FUNCTION_STRING = "function_string.txt"
    INPUTS = "inputs.pkl"
    ERROR = "error.log"
    EXECUTOR = "executor.pkl"
    RESULTS = "results.pkl"


class FileMapper(str, Enum):
    """Map module for mapping file module to their
    corresponding result from database"""

    ERROR = 3
    FUNCTION_STRING = 4
    EXECUTOR = 5
    INPUTS = 6
    RESULT = 7


class FileExtension(Enum):
    """Extension enum"""

    TXT = ".txt"
    PKL = ".pkl"
