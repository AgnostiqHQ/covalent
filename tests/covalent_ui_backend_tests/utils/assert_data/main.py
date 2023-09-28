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

"Main app mock data"


def main_mock_data():
    """Mock main data"""
    return {
        "test_webhook": {
            "api_path": "/api/webhook",
            "case1": {
                "status_code": 200,
                "response_data": {"ok": True},
            },
        },
        "test_draw": {
            "api_path": "/api/draw",
            "case1": {
                "status_code": 200,
                "response_data": {"ok": True},
            },
        },
        "test_misc": {
            "api_path": "/{}",
            "case1": {
                "path": {"rest_of_path": "logs"},
                "status_code": 200,
                "response_data": {"ok": True},
            },
        },
    }
