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

"""Lattice data"""

import os


def seed_lattice_data():
    """Mock db assert lattices data"""
    return {
        "test_lattices": {
            "api_path": "/api/v1/dispatches/{}",
            "case1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd"},
                "response_data": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "status": "COMPLETED",
                    "total_electrons": 6,
                    "total_electrons_completed": 6,
                    "started_at": "2022-09-23T15:31:11",
                    "ended_at": "2022-09-23T15:31:11",
                    "directory": os.path.abspath(
                        os.path.join(os.path.dirname(__file__), os.pardir)
                    )
                    + "/mock_files/"
                    + "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "description": None,
                    "runtime": 0,
                    "updated_at": None,
                },
            },
            "case_invalid_1": {
                "status_code": 400,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9c1"},
            },
            "case_invalid_2": {
                "status_code": 422,
                "path": {"dispatch_id": "123"},
            },
        },
        "test_lattices_file": {
            "api_path": "/api/v1/dispatches/{}/details/{}",
            "case_results_1": {
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "name": "result"},
                "status_code": 200,
                "response_data": {
                    "data": '"Hello shore  !!"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95\\x13\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x0fHello shore  !!\\x94.')",
                },
            },
            "case_function_string_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
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
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "name": "function",
                },
                "response_data": {
                    "data": '"<function hello at 0x7fcc2cdb4670>"',
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95&\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\"<function hello at 0x7fcc2cdb4670>\\x94.')",
                },
            },
            "case_inputs_1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "name": "inputs"},
                "response_data": {
                    "data": "{'args': (), 'kwargs': {'name': 'shore'}}",
                    "python_object": "import pickle\npickle.loads(b'\\x80\\x05\\x95(\\x00\\x00\\x00\\x00\\x00\\x00\\x00}\\x94(\\x8c\\x04args\\x94)\\x8c\\x06kwargs\\x94}\\x94\\x8c\\x04name\\x94\\x8c\\x05shore\\x94su.')",
                },
            },
            "case_error_1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "name": "error"},
                "response_data": {"data": "", "python_object": None},
            },
            "case_executor_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "name": "executor",
                },
                "response_data": {"executor_name": "dask", "executor_details": None},
            },
            "case_workflow_executor_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "name": "workflow_executor",
                },
                "response_data": {
                    "workflow_executor_name": "dask",
                    "workflow_executor_details": None,
                },
            },
            "case_transport_graph_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "name": "transport_graph",
                },
                "response_data": "'lattice_metadata': {'executor': 'dask', 'results_dir': '/home/arunmukesh/Desktop/files/results', 'workflow_executor': 'dask', 'deps': {}, 'call_before': [], 'call_after': [], 'executor_data': {}, 'workflow_executor_data': {}}, 'dirty_nodes': []",
            },
            "case_invalid_1": {
                "status_code": 422,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "name": "results",
                },
            },
            "case_bad_request": {
                "status_code": 400,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9c1",
                    "name": "result",
                },
            },
        },
        "test_sublattices": {
            "api_path": "/api/v1/dispatches/{}/sublattices",
            "case1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd"},
            },
            "case2": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd"},
                "query_data": {"sort_by": "total_electrons", "sort_direction": "ASC"},
            },
        },
        "functional_test_lattices": {
            "case1": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "lattice_id": 1}
        },
    }
