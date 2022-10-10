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

import tests.covalent_ui_backend_tests.utils.main as main
from tests.covalent_ui_backend_tests.utils.assert_data.settings import seed_settings_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_data = seed_settings_data()


def test_fetch_settings():
    """Test Fetch Settings"""
    test_data = output_data["test_settings"]["case1"]
    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    print(response.json())
    assert ("client" in response.json()) and ("server" in response.json())


def test_post_settings():
    """Test Post Settings"""
    test_data = output_data["test_settings"]["case2"]
    response = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_body"],
    )
    response2 = object_test_template(
        api_path=output_data["test_settings"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_body"],
        query_data=test_data["request_params"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]

    assert response2.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response2.json() == test_data["response_data"]
