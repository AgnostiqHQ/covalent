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

"""Lattice mock data"""

import os

from .config_data import INVALID_DISPATCH_ID, VALID_DISPATCH_ID


def seed_lattice_data():
    """Mock db assert lattices data"""
    lattice_end_date = "2022-10-27T10:08:43.877056"
    return {
        "test_lattices": {
            "api_path": "/api/v1/dispatches/{}",
            "case1": {
                "status_code": 200,
                "path": {"dispatch_id": VALID_DISPATCH_ID},
                "response_data": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "status": "COMPLETED",
                    "total_electrons": 6,
                    "total_electrons_completed": 6,
                    "started_at": "2022-09-23T10:01:11.155428",
                    "ended_at": "2022-09-23T10:01:11.717064",
                    "directory": os.path.abspath(
                        os.path.join(os.path.dirname(__file__), os.pardir)
                    )
                    + "/mock_files/"
                    + VALID_DISPATCH_ID,
                    "description": "",
                    "runtime": 0,
                    "updated_at": None,
                },
            },
            "case_invalid_1": {
                "status_code": 400,
                "path": {"dispatch_id": INVALID_DISPATCH_ID},
                "response_string": "does not exist",
            },
            "case_invalid_2": {
                "status_code": 422,
                "path": {"dispatch_id": "123"},
            },
        },
        "test_lattices_file": {
            "api_path": "/api/v1/dispatches/{}/details/{}",
            "case_results_1": {
                "path": {"dispatch_id": VALID_DISPATCH_ID, "name": "result"},
                "status_code": 200,
                "response_data": {
                    "data": '"Hello shore - lattice  !!"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x1d\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x19Hello shore - lattice  !!\\x94.')",
                },
            },
            "case_function_string_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "name": "function_string",
                },
                "response_data": {
                    "data": """@ct.lattice\ndef workflow(name):\n\tresult=join(hello(),moniker(name))\n\treturn result+\" !!\"""",
                    "python_object": None,
                },
            },
            "case_function_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "name": "function",
                },
                "response_data": {
                    "data": '"<function hello at 0x7fcc2cdb4670>"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95&\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\"<function hello at 0x7fcc2cdb4670>\\x94.')",
                },
            },
            "case_inputs_1": {
                "status_code": 200,
                "path": {"dispatch_id": VALID_DISPATCH_ID, "name": "inputs"},
                "response_data": {
                    "data": "{'args': (), 'kwargs': {'name': 'shore'}}",
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95(\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x04name\\x94\\x8c\\x05shore\\x94su.')",
                },
            },
            "case_error_1": {
                "status_code": 200,
                "path": {"dispatch_id": VALID_DISPATCH_ID, "name": "error"},
                "response_data": {"data": "", "python_object": None},
            },
            "case_executor_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "name": "executor",
                },
                "response_data": {"executor_name": "dask", "executor_details": {}},
            },
            "case_workflow_executor_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "name": "workflow_executor",
                },
                "response_data": {
                    "workflow_executor_name": "dask",
                    "workflow_executor_details": {},
                },
            },
            "case_transport_graph_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "name": "transport_graph",
                },
                "response_data": "'lattice_metadata': {'executor': 'dask', 'results_dir': '/home/arunmukesh/Desktop/files/results', 'workflow_executor': 'dask', 'deps': {}, 'call_before': [], 'call_after': [], 'executor_data': {}, 'workflow_executor_data': {}}, 'dirty_nodes': []",
            },
            "case_invalid_1": {
                "status_code": 422,
                "path": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "name": "results",
                },
                "response_message": "value is not a valid enumeration member; permitted: 'result', 'function_string', 'inputs', 'error', 'executor', 'workflow_executor', 'function', 'transport_graph'",
            },
            "case_bad_request": {
                "status_code": 400,
                "path": {
                    "dispatch_id": INVALID_DISPATCH_ID,
                    "name": "result",
                },
                "response_string": "does not exist",
            },
        },
        "test_sublattices": {
            "api_path": "/api/v1/dispatches/{}/sublattices",
            "case1": {
                "status_code": 200,
                "path": {"dispatch_id": "a95d84ad-c441-446d-83ae-46380dcdf38e"},
                "response_data": {
                    "sub_lattices": [
                        {
                            "dispatch_id": "69dec597-79d9-4c99-96de-8d5f06f3d4dd",
                            "lattice_name": "sub",
                            "runtime": 5000,
                            "total_electrons": 120,
                            "total_electrons_completed": 120,
                            "started_at": "2022-10-27T10:08:38.759335",
                            "ended_at": "2022-10-27T10:08:43.877056",
                            "status": "COMPLETED",
                            "updated_at": "2022-10-27T10:08:43.890454",
                        },
                        {
                            "dispatch_id": "89be0bcf-95dd-40a6-947e-6af6c56f147d",
                            "lattice_name": "sub",
                            "runtime": 1000,
                            "total_electrons": 20,
                            "total_electrons_completed": 20,
                            "started_at": "2022-10-27T10:08:34.497285",
                            "ended_at": "2022-10-27T10:08:35.997225",
                            "status": "COMPLETED",
                            "updated_at": "2022-10-27T10:08:36.004030",
                        },
                    ]
                },
            },
            "case2": {
                "status_code": 200,
                "path": {"dispatch_id": "a95d84ad-c441-446d-83ae-46380dcdf38e"},
                "query_data": {"sort_by": "total_electrons", "sort_direction": "ASC"},
                "response_data": {
                    "sub_lattices": [
                        {
                            "dispatch_id": "89be0bcf-95dd-40a6-947e-6af6c56f147d",
                            "lattice_name": "sub",
                            "runtime": 1000,
                            "total_electrons": 20,
                            "total_electrons_completed": 20,
                            "started_at": "2022-10-27T10:08:34.497285",
                            "ended_at": "2022-10-27T10:08:35.997225",
                            "status": "COMPLETED",
                            "updated_at": "2022-10-27T10:08:36.004030",
                        },
                        {
                            "dispatch_id": "69dec597-79d9-4c99-96de-8d5f06f3d4dd",
                            "lattice_name": "sub",
                            "runtime": 5000,
                            "total_electrons": 120,
                            "total_electrons_completed": 120,
                            "started_at": "2022-10-27T10:08:38.759335",
                            "ended_at": "2022-10-27T10:08:43.877056",
                            "status": "COMPLETED",
                            "updated_at": "2022-10-27T10:08:43.890454",
                        },
                    ]
                },
            },
        },
        "functional_test_lattices": {"case1": {"dispatch_id": VALID_DISPATCH_ID, "lattice_id": 1}},
    }
