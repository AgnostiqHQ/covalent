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

# Skip these since they cannot be tested in this way
ignore_files = [
    "construct_c_task.ipynb",
    "query_electron_execution_status.ipynb",
    "query_lattice_execution_status.ipynb",
    "visualize_lattice.ipynb",
    "cancel_dispatch.ipynb",
    "construct_bash_task.ipynb",
    "file_transfers_to_remote.ipynb",
    "file_transfers_to_from_remote.ipynb",
    "file_transfers_for_workflows_to_remote.ipynb",
    "creating_custom_executors.ipynb",
    "file_transfers_to_from_azure_blob.ipynb",
    "file_transfers_to_from_gcp_storage.ipynb",
    "file_transfers_for_workflows_to_remote.ipynb",
    "file_transfers_to_remote.ipynb",
    "trigger_sqlite.ipynb",  # TODO: Temp skip, see issue #1808
    "trigger_database.ipynb",  # TODO: Temp skip, see issue #1808
]


@pytest.mark.parametrize("file, expected_return_value", zip(files, expected_return_values))
def test_how_to_file(file, expected_return_value):
    if os.path.basename(file) not in ignore_files:
        proc = Popen(
            f"jupyter nbconvert {file} --to script --stdout | python",
            shell=True,
        )
        proc.communicate()
        assert proc.returncode == expected_return_value
