import json
from os.path import abspath, dirname

from utils.client_template import MethodType, TestClientTemplate
from utils.main import fastapi_app

object_test_template = TestClientTemplate()
output_path = dirname(abspath(__file__)) + "/utils/summary_data.json"
with open(output_path, "r") as output_json:
    output_data = json.load(output_json)


def test_overview():
    """Test overview"""
    response = object_test_template(
        path="/api/v1/dispatches/overview", app=fastapi_app, method_type=MethodType.GET
    )
    if "status_code" in output_data["test_overview"]["case1"]:
        assert response.status_code == output_data["test_overview"]["case1"]["status_code"]
    if "response_data" in output_data["test_overview"]["case1"]:
        res_data = response.json()
        assert res_data == output_data["test_overview"]["case1"]["response_data"]
