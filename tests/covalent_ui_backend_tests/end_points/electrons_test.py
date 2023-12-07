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

"""Electron test"""
import datetime

import pytest
from numpy import array

from covalent_dispatcher._db.datastore import DataStore

from .. import fastapi_app
from ..utils.assert_data.electrons import seed_electron_data
from ..utils.client_template import MethodType, TestClientTemplate
from ..utils.trigger_events import shutdown_event, startup_event

object_test_template = TestClientTemplate()
output_data = seed_electron_data()


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


@pytest.fixture(scope="module", autouse=True)
def env_setup():
    startup_event()
    mock_db()
    yield
    shutdown_event()


def test_electrons():
    """Test electrons API"""
    test_data = output_data["test_electrons"]["case1"]
    response = object_test_template(
        api_path=output_data["test_electrons"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        print("sam response ", response.json())
        print("sam data ", test_data["response_data"])
        assert response.json() == test_data["response_data"]


def test_electrons_bad_request():
    """Test electrons for details with bad request"""
    test_data = output_data["test_electrons"]["case_invalid"]
    response = object_test_template(
        api_path=output_data["test_electrons"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if "response_data" in test_data:
        assert response.json() == test_data["response_data"]


def test_electrons_details_hooks():
    """Test electrons for hooks details"""
    test_data = output_data["test_electrons_details"]["case_hooks_1"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=fastapi_app,
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
        app=fastapi_app,
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
        app=fastapi_app,
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
#         app=fastapi_app,
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
#         app=fastapi_app,
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
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]


def test_electrons_inputs_bad_request():
    """Test electrons for inputs with bad request"""
    test_data = output_data["test_electrons_details"]["case_invalid"]
    response = object_test_template(
        api_path=output_data["test_electrons_details"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    if test_data["response_data"]:
        assert response.json() == test_data["response_data"]


mock_input_data_jobs = {
    "circuit_0@b72cce1f-a73f-4f3e-8de2-c31cf1d5092f": {
        "electron_node_id": "0",
        "dispatch_id": "e8fd09c9-1406-4686-9e77-c8d4d64a76ee",
        "circuit_name": "qkernel",
        "circuit_description": None,
        "circuit_diagram": "0: ──RX──RX─┤ ╭Probs\n1: ──RX──RX─┤ ├Probs\n2: ──RX──RX─┤ ├Probs\n3: ──RX──RX─┤ ├Probs\n4: ──RX──RX─┤ ╰Probs",
        "qnode_specs": {
            "gate_sizes": {"5": 2},
            "gate_types": {"AngleEmbedding": 1, "Adjoint(AngleEmbedding)": 1},
            "num_operations": 2,
            "num_observables": 1,
            "num_diagonalizing_gates": 0,
            "num_used_wires": 5,
            "depth": 2,
            "num_trainable_params": 0,
            "num_device_wires": 5,
            "device_name": "qe_device",
            "diff_method": "best",
            "expansion_strategy": "gradient",
            "gradient_options": {},
            "interface": "auto",
            "gradient_fn": "none",
            "num_gradient_executions": 0,
            "num_parameter_shift_executions": None,
        },
        "qexecutor": {
            "persist_data": True,
            "qnode_device_import_path": "pennylane.devices.default_qubit:DefaultQubit",
            "qnode_device_shots": None,
            "qnode_device_wires": 5,
            "pennylane_active_return": True,
            "device": "default.qubit",
            "parallel": "thread",
            "workers": 10,
            "shots": 0,
            "name": "Simulator",
            "_backend": {
                "persist_data": True,
                "qnode_device_import_path": "pennylane.devices.default_qubit:DefaultQubit",
                "qnode_device_shots": None,
                "qnode_device_wires": 5,
                "pennylane_active_return": True,
                "device": "default.qubit",
                "num_threads": 10,
                "name": "BaseThreadPoolQExecutor",
            },
        },
        "save_time": datetime.datetime(2023, 8, 11, 15, 38, 55, 798495),
        "circuit_id": "circuit_0@b72cce1f-a73f-4f3e-8de2-c31cf1d5092f",
        "qscript": "RX!8.692890013151683![0]RX!1.5432201574818243![1]RX!9.785937231907651![2]RX!3.148843240541814![3]RX!4.573246180972299![4]RX!0.9098741371966934![4]RX!2.7169925354199522![3]RX!11.084343055037124![2]RX!-9.685382030597465![1]RX!5.623777349527314![0]|||ObservableReturnTypes.Probability!Identity[0, 1, 2, 3, 4]",
        "execution_time": 0.0021365240000363883,
        "result": [
            array(
                [
                    0.0337228,
                    0.00602918,
                    0.00151217,
                    0.00027036,
                    0.08562897,
                    0.0153093,
                    0.00383971,
                    0.00068649,
                    0.06050233,
                    0.010817,
                    0.002713,
                    0.00048505,
                    0.1536276,
                    0.02746654,
                    0.00688885,
                    0.00123163,
                    0.04838155,
                    0.00864997,
                    0.00216949,
                    0.00038787,
                    0.12285049,
                    0.02196401,
                    0.00550876,
                    0.00098489,
                    0.08680171,
                    0.01551897,
                    0.00389229,
                    0.00069589,
                    0.22040701,
                    0.0394058,
                    0.00988331,
                    0.001767,
                ]
            )
        ],
        "result_metadata": {
            "execution_metadata": [[]],
            "device_name": "default.qubit",
            "executor_name": "BaseThreadPoolQExecutor",
            "executor_backend_name": "",
        },
    }
}


@pytest.fixture
def qelectron_mocked_data_for_jobs(mocker):
    from covalent.quantum.qserver.database import Database

    return mocker.patch.object(Database, "get_db_dict", return_value=mock_input_data_jobs)


def test_get_qelectrons_jobs(qelectron_mocked_data_for_jobs):
    test_data = output_data["test_get_qelectrons_jobs"]["case_1"]
    response = object_test_template(
        api_path=output_data["test_get_qelectrons_jobs"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    assert response.json() == test_data["response_data"]


def test_get_qelectron_job_detail(qelectron_mocked_data_for_jobs):
    test_data = output_data["test_get_qelectron_job_detail"]["case_1"]
    response = object_test_template(
        api_path=output_data["test_get_qelectron_job_detail"]["api_path"],
        app=fastapi_app,
        method_type=MethodType.GET,
        path=test_data["path"],
    )
    assert response.status_code == test_data["status_code"]
    assert response.json() == test_data["response_data"]
