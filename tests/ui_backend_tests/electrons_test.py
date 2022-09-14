import json
from os.path import abspath, dirname

import tests.ui_backend_tests.utils.main as main
from tests.ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/electrons_data.json"
with open(output_path, "r") as output_json:
    output_data = json.load(output_json)


def test_electrons():
    """Test electrons"""
    test_data = output_data["test_electrons"]["case1"]
    response = object_test_template(
        path=output_data["test_electrons"]["path"],
        app=main.fastapi_app,
        method_type=MethodType.GET,
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


# def test_electrons_details_function_string():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_function_string"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_function_string"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_executor():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_executor"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_executor"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_result():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_result"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_result"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_value():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_value"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_value"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_stdout():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_stdout"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_stdout"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_deps():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_deps"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_deps"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_call_before():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_call_before"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_call_before"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_call_after():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_call_after"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_call_after"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_call_error():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_call_error"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_call_error"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_info():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_info"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_info"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_electrons_details_inputs():
#     """Test overview"""
#     test_data = output_data["test_electrons_details_inputs"]["case1"]
#     response = object_test_template(
#         path=output_data["test_electrons_details_inputs"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET,
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]
