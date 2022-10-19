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

"""Graph test"""

import tests.covalent_ui_backend_tests.utils.main as main
from tests.covalent_ui_backend_tests.utils.assert_data.graph import seed_graph_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_data = seed_graph_data()


def test_get_graph():
    """test get graph"""
    test_data = output_data["test_graph"]["case_test_get_graph"]
    response = object_test_template(
        api_path=output_data["test_graph"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_graph_invalid_dispatch_id():
    """test graph invalid dispatch id"""
    test_data = output_data["test_graph"]["case_test_graph_invalid_dispatch_id"]
    response = object_test_template(
        api_path=output_data["test_graph"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]
