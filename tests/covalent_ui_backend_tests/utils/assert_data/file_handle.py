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

"File Handler mock data"


def mock_file_data():
    """Mock main data"""
    return {
        "test_read_text": {
            "file_path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd",
            "case1": {
                "file_name": "function_string.txt",
                "response_data": """@ct.lattice
def workflow(name):
\tresult=join(hello(),moniker(name))
\treturn result+" !!\"""",
            },
            "case2": {"file_name": "function_strings.txt", "response_data": None},
        },
        "test_unpickle": {
            "file_path": "tests/covalent_ui_backend_tests/utils/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd",
            "case1": {
                "file_name": "result.pkl",
                "response_data": (None, None),
            },
        },
    }
