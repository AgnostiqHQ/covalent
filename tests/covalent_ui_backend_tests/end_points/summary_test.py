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

from os.path import abspath, dirname

import tests.covalent_ui_backend_tests.utils.main as main
from tests.covalent_ui_backend_tests.utils.assert_data.summary import seed_summary_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/assert_data/summary_data.json"
output_data = seed_summary_data()


def test_overview():
    """Test overview"""
    test_data = output_data["test_overview"]["case1"]
    response = object_test_template(
        api_path=output_data["test_overview"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_overview_invalid_method():
    """Test overview with post method"""
    test_data = output_data["test_overview"]["case2"]
    response = object_test_template(
        api_path=output_data["test_overview"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list():
    """Test list"""
    test_data = output_data["test_list"]["case1"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list_count():
    """Test list"""
    test_data = output_data["test_list"]["case2"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list_invalid_count():
    """Test list"""
    test_data = output_data["test_list"]["case4"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list_search():
    """Test list"""
    test_data = output_data["test_list"]["case2"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list_invalid_offset():
    """Test List with invalid offset"""
    test_data = output_data["test_list"]["case3"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    response_detail = response.json()["detail"][0]
    assert response_detail["type"] == "value_error.number.not_gt"


def test_delete():
    """Test delete from dispatch list"""
    test_data = output_data["test_delete"]["case1"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_invalid_dispatch_id():
    """Test delete from dispatch list"""
    test_data = output_data["test_delete"]["case2"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_dispatch_multiple_times():
    """Test delete from dispatch list"""
    test_data = output_data["test_delete"]["case3"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_invalid_uuid():
    """Test List with invalid offset"""
    test_data = output_data["test_delete"]["case4"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    response_detail = response.json()["detail"][0]
    assert response_detail["type"] == "type_error.uuid"


def test_delete_all():
    """Test delete all dispatches"""
    test_data = output_data["test_delete_all"]["case1"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_all_with_search():
    """Test delete all dispatches with search"""
    test_data = output_data["test_delete_all"]["case2"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_all_invalid_filter():
    """Test delete all dispatches with search"""
    test_data = output_data["test_delete_all"]["case3"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    response_detail = response.json()["detail"][0]
    assert response_detail["type"] == "type_error.enum"
