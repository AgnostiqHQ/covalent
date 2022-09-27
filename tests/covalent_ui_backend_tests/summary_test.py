from os.path import abspath, dirname

import tests.covalent_ui_backend_tests.utils.main as main
from tests.covalent_ui_backend_tests.utils.assert_data.summary import seed_summary_data
from tests.covalent_ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/assert_data/summary_data.json"
# with open(output_path, "r") as output_json:
#     output_data = json.load(output_json)
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
    print(response.json())
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
