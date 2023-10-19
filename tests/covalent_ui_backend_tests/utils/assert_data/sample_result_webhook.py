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

"Result Webhook mock data"


def result_mock_data():
    """Mock data for result webhook"""
    return {
        "test_result_webhooks": {
            "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
            "case1": {
                "test_path": "/api/draw",
                "response_data": "http://localhost:48008/api/draw",
            },
        }
    }
