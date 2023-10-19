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

"""Lattices test"""
from os.path import abspath, dirname

import pytest

from .. import fastapi_app
from ..utils.assert_data.lattices import seed_lattice_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/assert_data/lattices_data.json"
output_data = seed_lattice_data()


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


def test_lattices():
    """Test lattices AP"""
    test_data = output_data["test_lattices"]["case1"]
    response = object_test_template(
        api_path=output_data["test_lattices"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


@pytest.mark.skip(reason="Test is breaking, need to fix, see PR #1728")
def test_lattices_transport_graph():
    """Test lattices for transport graph"""
    test_data = output_data["test_lattices_file"]["case_transport_graph_1"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]


def test_lattices_file_bad_request():
    """Test lattices results"""
    test_data = output_data["test_lattices_file"]["case_bad_request"]
    response = object_test_template(
        api_path=output_data["test_lattices_file"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
        query_data=test_data["query_data"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_data"]:
        assert response.json() == test_data["response_data"]
