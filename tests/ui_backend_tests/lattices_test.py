import json
from os.path import abspath, dirname

import tests.ui_backend_tests.utils.main as main
from tests.ui_backend_tests.utils.client_template import MethodType, TestClientTemplate

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/lattices_data.json"
with open(output_path, "r") as output_json:
    output_data = json.load(output_json)


def test_lattices():
    """Test lattices results"""
    test_data = output_data["test_lattices"]["case1"]
    response = object_test_template(
        path=output_data["test_lattices"]["path"], app=main.fastapi_app, method_type=MethodType.GET
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


# def test_lattices_results():
#     """Test lattices results"""
#     test_data = output_data["test_lattices_results"]["case1"]
#     response = object_test_template(
#         path=output_data["test_lattices_results"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_lattices_function_string():
#     """Test lattices results"""
#     test_data = output_data["test_lattices_function_string"]["case1"]
#     response = object_test_template(
#         path=output_data["test_lattices_function_string"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]

# def test_lattices_function_inputs():
#     """Test lattices results"""
#     test_data = output_data["test_lattices_function_inputs"]["case1"]
#     response = object_test_template(
#         path=output_data["test_lattices_function_inputs"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_lattices_function_errors():
#     """Test lattices results"""
#     test_data = output_data["test_lattices_function_errors"]["case1"]
#     response = object_test_template(
#         path=output_data["test_lattices_function_errors"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_lattices_function_executor():
#     """Test lattices results"""
#     test_data = output_data["test_lattices_function_executor"]["case1"]
#     response = object_test_template(
#         path=output_data["test_lattices_function_executor"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]


# def test_lattices_function_workflow_executor():
#     """Test lattices results"""
#     test_data = output_data["test_lattices_function_workflow_executor"]["case1"]
#     response = object_test_template(
#         path=output_data["test_lattices_function_workflow_executor"]["path"],
#         app=main.fastapi_app,
#         method_type=MethodType.GET
#     )
#     assert response.status_code == test_data["status_code"]
#     if "response_data" in test_data:
#         assert response.json() == test_data["response_data"]
