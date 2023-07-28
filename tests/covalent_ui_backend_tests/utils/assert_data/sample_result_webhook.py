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
