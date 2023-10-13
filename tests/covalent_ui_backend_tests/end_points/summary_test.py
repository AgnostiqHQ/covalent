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

"""Summary Test"""


from os.path import abspath, dirname

import pytest
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import declarative_base

from .. import fastapi_app
from ..utils.assert_data.summary import seed_summary_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
MockBase = declarative_base()
output_path = f"{dirname(abspath(__file__))}/utils/assert_data/summary_data.json"
output_data = seed_summary_data()


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    yield
    shutdown_event()


class MockLattice(MockBase):
    """Mock Lattice"""

    __tablename__ = "lattices"
    id = Column(Integer, primary_key=True)
    dispatch_id = Column(String(2), nullable=False)
    electron_id = Column(Integer)
    status = Column(String(24), nullable=False)
    name = Column(String(24), nullable=False)
    electron_num = Column(Integer, nullable=False)
    completed_electron_num = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, onupdate=func.now(), server_default=func.now())
    started_at = Column(DateTime)
    completed_at = Column(DateTime)


@pytest.mark.skip(reason="TODO: Need to fix this test. See failing tests in PR #1778.")
def test_overview():
    """Test overview"""
    test_data = output_data["test_overview"]["case1"]
    response = object_test_template(
        api_path=output_data["test_overview"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list_count():
    """Test list count"""
    test_data = output_data["test_list"]["case2"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_list_invalid_count():
    """Test list with invalid count"""
    test_data = output_data["test_list"]["case4"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]


def test_list_search():
    """Test list with search"""
    test_data = output_data["test_list"]["case2"]
    response = object_test_template(
        api_path=output_data["test_list"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        query_data=test_data["request_data"]["query"],
    )
    assert response.status_code == test_data["status_code"]


def test_delete():
    """Test delete from dispatch list"""
    test_data = output_data["test_delete"]["case1"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_dispatch_multiple_times():
    """Test delete multiple dispatches list"""
    test_data = output_data["test_delete"]["case3"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_invalid_uuid():
    """Test List with invalid UUID"""
    test_data = output_data["test_delete"]["case4"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]


def test_delete_empty():
    """Test deleting empty dispatches"""
    test_data = output_data["test_delete"]["case5"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_none():
    """Test deleting with NULL value"""
    test_data = output_data["test_delete"]["case6"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_partial_delete():
    """Test deleting with partial dispatches"""
    test_data = output_data["test_delete"]["case8"]
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_bad_request(mocker):
    """Test deleting with bad request"""
    test_data = output_data["test_delete"]["case7"]
    mocker.patch("covalent_ui.api.v1.data_layer.summary_dal.Lattice", MockLattice)
    response = object_test_template(
        api_path=output_data["test_delete"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_all():
    """Test delete all dispatches"""
    test_data = output_data["test_delete_all"]["case1"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_all_with_search():
    """Test delete all dispatches with search"""
    test_data = output_data["test_delete_all"]["case3"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_delete_all_with_filter():
    """Test delete all dispatches with filter"""
    test_data = output_data["test_delete_all"]["case2"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]


def test_delete_all_with_filter_case2():
    """Test delete all dispatches with filter case2"""
    test_data = output_data["test_delete_all"]["case4"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]


def test_delete_all_invalid_filter():
    """Test delete all dispatches with invalid filter"""
    test_data = output_data["test_delete_all"]["case5"]
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]


def test_delete_all_bad_request(mocker):
    """Test delete all dispatches with bad request"""
    test_data = output_data["test_delete_all"]["case6"]
    mocker.patch("covalent_ui.api.v1.data_layer.summary_dal.Lattice", MockLattice)
    response = object_test_template(
        api_path=output_data["test_delete_all"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.POST,
        body_data=test_data["request_data"]["body"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]
