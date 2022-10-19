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
