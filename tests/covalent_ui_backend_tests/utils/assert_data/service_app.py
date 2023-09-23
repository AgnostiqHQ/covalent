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

"Service app mock data"


def seed_service_app_data():
    return {
        "test_result": {
            "api_path": "/api/result/83568425-5565-4543-ab6f-7afb88e50458?wait=false&status_only=false",
            "case1": {
                "status_code": 404,
                "response_data": {
                    "message": "The requested dispatch ID 78525234-72ec-42dc-94a0-f4751707f9cd was not found."
                },
            },
        },
        "test_db_path": {
            "api_path": "/api/db-path",
            "case1": {
                "status_code": 200,
                "response_data": '"/home/arunmukesh/.local/share/covalent/dispatcher_db.sqlite"',
            },
        },
    }
