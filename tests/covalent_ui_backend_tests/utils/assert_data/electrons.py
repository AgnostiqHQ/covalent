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

"Electrons mock data"

import os

from .config_data import INVALID_DISPATCH_ID, INVALID_NODE_ID, VALID_DISPATCH_ID, VALID_NODE_ID


def seed_electron_data():
    """Mock db electron data"""
    return {
        "test_electrons": {
            "api_path": "/api/v1/dispatches/{}/electron/{}",
            "case1": {
                "status_code": 200,
                "path": {"dispatch_id": VALID_DISPATCH_ID, "electron_id": VALID_NODE_ID},
                "response_data": {
                    "id": 1,
                    "node_id": 0,
                    "parent_lattice_id": 1,
                    "type": "function",
                    "storage_path": os.path.abspath(
                        os.path.join(os.path.dirname(__file__), os.pardir)
                    )
                    + f"/mock_files/{VALID_DISPATCH_ID}/node_{VALID_NODE_ID}",
                    "name": "hello",
                    "status": "COMPLETED",
                    "started_at": "2022-09-23T10:01:11.168972",
                    "ended_at": "2022-09-23T10:01:11.483405",
                    "runtime": 0,
                    "description": "",
                    "qelectron": None,
                    "qelectron_data_exists": False,
                },
            },
            "case_invalid": {
                "status_code": 400,
                "path": {"dispatch_id": INVALID_DISPATCH_ID, "electron_id": INVALID_NODE_ID},
                "response_data": {
                    "detail": [
                        {
                            "loc": ["path", "dispatch_id"],
                            "msg": f"Dispatch ID {INVALID_DISPATCH_ID} or Electron ID does not exist",
                            "type": None,
                        }
                    ]
                },
            },
        },
        "test_electrons_details": {
            "api_path": "/api/v1/dispatches/{}/electron/{}/details/{}",
            "case_function_string_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "function_string",
                },
                "response_data": {
                    "data": '@ct.electron\ndef hello(): return "Hello "\n"\n                    ',
                    "python_object": None,
                },
            },
            "case_function_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "function",
                },
                "response_data": {
                    "data": '"<function hello at 0x7fcc2cdb4670>"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95&\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\"<function hello at 0x7fcc2cdb4670>\\x94.')",
                },
            },
            "case_executor_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "executor",
                },
                "response_data": {"executor_name": "dask", "executor_details": {}},
            },
            "case_result_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "result",
                },
                "response_data": {
                    "data": '"Hello shore - Node 0 !!"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1b\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x17Hello shore - Node 0 !!\\x94.')",
                },
            },
            "case_value_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "value",
                },
                "response_data": {"data": "(None, None)", "python_object": None},
            },
            "case_stdout_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "stdout",
                },
                "response_data": {
                    "data": "DEBUG: update_electrons_data called on node 5\nDEBUG: update_electrons_data called on node 1",
                    "python_object": None,
                },
            },
            "case_hooks_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "hooks",
                },
                "response_data": {"data": None, "python_object": None},
            },
            "case_error_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "error",
                },
                "response_data": {"data": "", "python_object": None},
            },
            "case_error_2": {
                "status_code": 400,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "inputs",
                },
                "response_data": {
                    "detail": [
                        {
                            "loc": ["path", "dispatch_id"],
                            "msg": f"Dispatch ID {VALID_DISPATCH_ID} or Electron ID does not exist",
                            "type": None,
                        }
                    ]
                },
            },
            "case_info_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "info",
                },
                "response_data": {"data": None, "python_object": None},
            },
            "case_inputs_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "inputs",
                },
                "response_data": {
                    "data": "{'args': [], 'kwargs': {}}",
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x19\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94]\\x94\\x8c\\x06kwargs\\x94}\\x94u.')",
                },
            },
            "case_bad_request": {
                "status_code": 422,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "electron_id": VALID_NODE_ID,
                    "name": "results",
                },
                "response_message": "value is not a valid enumeration member; permitted: 'function_string', 'function', 'executor', 'result', 'value', 'stdout', 'hooks', 'error', 'info', 'inputs'",
            },
            "case_invalid": {
                "status_code": 400,
                "path": {
                    "dispatch_id": INVALID_DISPATCH_ID,
                    "electron_id": INVALID_NODE_ID,
                    "name": "function_string",
                },
                "response_data": {
                    "detail": [
                        {
                            "loc": ["path", "dispatch_id"],
                            "msg": f"Dispatch ID {INVALID_DISPATCH_ID} or Electron ID does not exist",
                            "type": None,
                        }
                    ]
                },
            },
        },
        "test_get_qelectrons_jobs": {
            "api_path": "/api/v1/dispatches/{}/electron/{}/jobs",
            "case_1": {
                "status_code": 200,
                "path": {"dispatch_id": "e8fd09c9-1406-4686-9e77-c8d4d64a76ee", "node_id": 0},
                "response_data": [
                    {
                        "job_id": "circuit_0@b72cce1f-a73f-4f3e-8de2-c31cf1d5092f",
                        "start_time": "2023-08-11T15:38:55.798495",
                        "executor": "BaseThreadPoolQExecutor",
                        "status": "COMPLETED",
                    }
                ],
            },
        },
        "test_get_qelectron_job_detail": {
            "api_path": "/api/v1/dispatches/{}/electron/{}/jobs/{}",
            "case_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "e8fd09c9-1406-4686-9e77-c8d4d64a76ee",
                    "node_id": 0,
                    "job_id": "circuit_0@b72cce1f-a73f-4f3e-8de2-c31cf1d5092f",
                },
                "response_data": {
                    "overview": {
                        "job_name": "qkernel",
                        "backend": "",
                        "time_elapsed": 0.0021365240000363883,
                        "result": "array([0.0337228 , 0.00602918, 0.00151217, 0.00027036, 0.08562897,\n       0.0153093 , 0.00383971, 0.00068649, 0.06050233, 0.010817  ,\n       0.002713  , 0.00048505, 0.1536276 , 0.02746654, 0.00688885,\n       0.00123163, 0.04838155, 0.00864997, 0.00216949, 0.00038787,\n       0.12285049, 0.02196401, 0.00550876, 0.00098489, 0.08680171,\n       0.01551897, 0.00389229, 0.00069589, 0.22040701, 0.0394058 ,\n       0.00988331, 0.001767  ])",
                        "status": "COMPLETED",
                        "start_time": "2023-08-11T15:38:55.798495",
                        "end_time": "2023-08-11T15:38:55.800632",
                    },
                    "circuit": {
                        "total_qbits": 5,
                        "depth": 2,
                        "circuit_diagram": "0: ──RX──RX─┤ ╭Probs\n1: ──RX──RX─┤ ├Probs\n2: ──RX──RX─┤ ├Probs\n3: ──RX──RX─┤ ├Probs\n4: ──RX──RX─┤ ╰Probs",
                        "qbit5_gates": 2,
                    },
                    "executor": {
                        "name": "Simulator",
                        "executor": "{'persist_data': True, 'qnode_device_import_path': 'pennylane.devices.default_qubit:DefaultQubit', 'qnode_device_shots': None, 'qnode_device_wires': 5, 'pennylane_active_return': True, 'device': 'default.qubit', 'parallel': 'thread', 'workers': 10, 'shots': 0, 'name': 'Simulator', '_backend': {'persist_data': True, 'qnode_device_import_path': 'pennylane.devices.default_qubit:DefaultQubit', 'qnode_device_shots': None, 'qnode_device_wires': 5, 'pennylane_active_return': True, 'device': 'default.qubit', 'num_threads': 10, 'name': 'BaseThreadPoolQExecutor'}}",
                    },
                },
            },
        },
    }
