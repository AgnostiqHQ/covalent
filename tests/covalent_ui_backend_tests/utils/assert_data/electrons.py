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


import os


def seed_electron_data():
    """Mock db electron data"""
    return {
        "test_electrons": {
            "api_path": "/api/v1/dispatches/{}/electron/{}",
            "case1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "electron_id": 0},
                "response_data": {
                    "id": 1,
                    "node_id": 0,
                    "parent_lattice_id": 1,
                    "type": "function",
                    "storage_path": os.path.abspath(
                        os.path.join(os.path.dirname(__file__), os.pardir)
                    )
                    + "/mock_files/78525234-72ec-42dc-94a0-f4751707f9cd/node_0",
                    "name": "hello",
                    "status": "COMPLETED",
                    "started_at": "2022-09-23T15:31:11",
                    "ended_at": "2022-09-23T15:31:11",
                    "runtime": 0,
                    "description": "",
                },
            },
            "case_invalid": {
                "status_code": 400,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "electron_id": 8},
            },
        },
        "test_electrons_details": {
            "api_path": "/api/v1/dispatches/{}/electron/{}/details/{}",
            "case_function_string_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
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
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "function",
                },
                "response_data": {
                    "data": None,
                    "python_object": None,
                },
            },
            "case_executor_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "executor",
                },
                "response_data": {"executor_name": "dask", "executor_details": None},
            },
            "case_result_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "result",
                },
                "response_data": {
                    "data": '"Hello shore  !!"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x13\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x0fHello shore  !!\\x94.')",
                },
            },
            "case_value_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "value",
                },
                "response_data": {"data": "(None, None)", "python_object": None},
            },
            "case_stdout_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "stdout",
                },
                "response_data": {
                    "data": "DEBUG: update_electrons_data called on node 5\nDEBUG: update_electrons_data called on node 1",
                    "python_object": None,
                },
            },
            "case_deps_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "deps",
                },
                "response_data": {"data": None, "python_object": None},
            },
            "case_call_before_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "call_before",
                },
                "response_data": {"data": "", "python_object": None},
            },
            "case_call_after_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "call_after",
                },
                "response_data": {"data": "", "python_object": None},
            },
            "case_error_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "error",
                },
                "response_data": {"data": "", "python_object": None},
            },
            "case_info_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "info",
                },
                "response_data": {"data": "", "python_object": None},
            },
            "case_inputs_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "inputs",
                },
                "response_data": {"data": '{"args": [], "kwargs": {}}'},
            },
            "case_bad_request": {
                "status_code": 422,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "results",
                },
            },
        },
    }
