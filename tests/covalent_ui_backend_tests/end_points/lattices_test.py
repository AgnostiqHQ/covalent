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
from tests.covalent_ui_backend_tests.utils.assert_data.lattices import seed_lattice_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/assert_data/lattices_data.json"
output_data = seed_lattice_data()


def test_lattices():
    """Test lattices results"""
    test_data = output_data["test_lattices"]["case1"]
    response = object_test_template(
        api_path=output_data["test_lattices"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_bad_request():
    """Test lattices results"""
    test_data = output_data["test_lattices"]["case_invalid_1"]
    response = object_test_template(
        api_path=output_data["test_lattices"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_string"]:
        response_detail = response.json()["detail"][0]
        assert test_data["response_string"] in response_detail["msg"]


def test_lattices_results():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_results_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_function_string():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_function_string_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_function():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_function_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_inputs():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_inputs_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_function_errors():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_error_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_function_executor():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_executor_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_function_workflow_executor():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_workflow_executor_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_lattices_transport_graph():
    """Test lattices for transport graph"""
    test_data = output_data["test_lattices_file"]["case_transport_graph_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert test_data["response_data"] in response.json()["data"]


def test_lattices_invalid_name():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_invalid_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_type"]:
        response_detail = response.json()["detail"][0]
        assert response_detail["type"] == test_data["response_type"]


def test_lattices_file_bad_request():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_bad_request"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_string"]:
        response_detail = response.json()["detail"][0]
        assert test_data["response_string"] in response_detail["msg"]


def test_sublattices():
    """Test sublattices"""
    test_data = output_data["test_sublattices"]["case1"]
    response = object_test_template(
        api_path=output_data["test_sublattices"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_data"]:
        assert response.json() == test_data["response_data"]


def test_sublattices_queries():
    """Test sublattices with queries"""
    test_data = output_data["test_sublattices"]["case2"]
    response = object_test_template(
        api_path=output_data["test_sublattices"]["api_path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
        query_data=test_data["query_data"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_data"]:
        assert response.json() == test_data["response_data"]
