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

import glob
import os
from subprocess import Popen

import pytest

import covalent as ct

rootdir = os.path.dirname(ct.__file__)
how_to_dir = "/../doc/source/how_to/**/"
suffix = "*.ipynb"
files = glob.glob(rootdir + how_to_dir + suffix, recursive=True)
expected_return_values = [0] * len(files)

# Skip these since they require graphviz and/or gcc
ignore_files = [
    "construct_c_task.ipynb",
    "query_electron_execution_status.ipynb",
    "query_lattice_execution_status.ipynb",
    "visualize_lattice.ipynb",
    "cancel_dispatch.ipynb",
    "construct_bash_task.ipynb",
]


@pytest.mark.parametrize("file,expected_return_value", zip(files, expected_return_values))
def test_how_to_file(file, expected_return_value):
    if os.path.basename(file) not in ignore_files:
        proc = Popen(
            f"jupyter nbconvert {file} --to script --stdout | python",
            shell=True,
        )
        proc.communicate()
        assert proc.returncode == expected_return_value
