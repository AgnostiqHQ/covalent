# Copyright 2023 Agnostiq Inc.
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

"""Test http file transfer."""

import covalent as ct


def test_http_file_transfer():
    """Test http file transfer."""

    @ct.electron(
        files=[
            ct.fs.TransferFromRemote(
                "https://raw.githubusercontent.com/curran/data/gh-pages/dataSoup/datasets.csv"
            ),
        ]
    )
    def get_remote_file(files=[]):
        source_path, dest_path = files[0]
        with open(dest_path, "r") as f:
            return f.read()

    @ct.lattice
    def workflow():
        return get_remote_file()

    dispatch_id = ct.dispatch(workflow)()
    res = ct.get_result(dispatch_id, wait=True)
    result_string = res.result

    assert result_string[:12] == "Dataset Name"
    assert result_string[-12:] == "05,,JSON,,,,"
    assert len(result_string) == 9248
    assert res.status == "COMPLETED"
