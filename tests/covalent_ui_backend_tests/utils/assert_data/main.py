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
