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

"""Electron test"""
import pytest

import tests.covalent_ui_backend_tests.utils.main as main
from covalent_dispatcher._db.datastore import DataStore
from tests.covalent_ui_backend_tests.utils.assert_data.electrons import seed_electron_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_data = seed_electron_data()


@pytest.fixture
def mock_db():
    """Instantiate and return an in-memory database."""
    import pathlib

    mock_db_path = (
        str(pathlib.Path(__file__).parent.parent.absolute()) + "/utils/data/mock_db.sqlite"
    )
    return DataStore(
        db_URL="sqlite+pysqlite:///" + mock_db_path,
        initialize_db=True,
    )


def test_electrons():
    """Test electrons API"""
    test_data = output_data["test_electrons"]["case1"]
    response = object_test_template(
        api_path=output_data["test_electrons"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_bad_request():
    """Test electrons for details with bad request"""
    test_data = output_data["test_electrons"]["case_invalid"]
    response = object_test_template(
        api_path=output_data["test_electrons"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_data"]:
        assert response.json() == test_data["response_data"]


def test_electrons_details_function_string():
    """Test electrons for function string details"""
    test_data = output_data["test_electrons_details"]["case_function_string_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        path=test_data["path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_function():
    """Test electrons for function details"""
    test_data = output_data["test_electrons_details"]["case_function_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        path=test_data["path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_executor():
    """ "Test electrons for executor details"""
    test_data = output_data["test_electrons_details"]["case_executor_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_result():
    """Test electrons for result details"""
    test_data = output_data["test_electrons_details"]["case_result_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_value():
    """Test electrons for value details"""
    test_data = output_data["test_electrons_details"]["case_value_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_stdout():
    """Test electrons for stdout details"""
    test_data = output_data["test_electrons_details"]["case_stdout_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_deps():
    """Test electrons for deps details"""
    test_data = output_data["test_electrons_details"]["case_deps_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_call_before():
    """Test electrons for call_before details"""
    test_data = output_data["test_electrons_details"]["case_call_before_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_call_after():
    """Test electrons for call_after details"""
    test_data = output_data["test_electrons_details"]["case_call_after_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_call_error():
    """Test electrons for error details"""
    test_data = output_data["test_electrons_details"]["case_error_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_info():
    """Test electrons for info details"""
    test_data = output_data["test_electrons_details"]["case_info_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


# def test_electrons_details_inputs():
#     """Test overview"""
#     test_data = output_data["test_electrons_details"]["case_inputs_1"]
#     response = object_test_template(
#         api_path=output_data["test_electrons_details"]["api_path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#         path=test_data["path"],
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_inputs_json(mocker):
#     """Test electrons with detailed inputs with JSON data"""
#     mocker.patch("covalent_dispatcher._service.app.workflow_db", DataStore())
#     test_data = output_data["test_electrons_details"]["case_error_2"]
#     response = object_test_template(
#         api_path=output_data["test_electrons_details"]["api_path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#         path=test_data["path"],
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


def test_electrons_file_bad_request():
    """Test electrons file with bad request"""
    test_data = output_data["test_electrons_details"]["case_bad_request"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    response_detail = response.json()["detail"][0]
    assert response_detail["type"] == "type_error.enum"


def test_electrons_inputs_bad_request():
    """Test electrons for inputs with bad request"""
    test_data = output_data["test_electrons_details"]["case_invalid"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_data"]:
        assert response.json() == test_data["response_data"]
