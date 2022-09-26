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
                    "directory": os.path.abspath(  # os.path.dirname(__file__)
                        os.path.join(os.path.dirname(__file__), os.pardir)
                    )
                    + "/mock_results/"
                    + "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "description": None,
                    "runtime": 0,
                    "updated_at": None,
                },
            },
        },
        "test_lattices_file": {
            "api_path": "/api/v1/dispatches/{}/details/{}",
            "case_results_1": {
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "name": "result"},
                "status_code": 200,
                "response_data": {"data": '"Hello shore  !!"'},
            },
            "case_function_string_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "name": "function_string",
                },
                "response_data": {
                    "data": """@ct.lattice\ndef workflow(name):\n\tresult=join(hello(),moniker(name))\n\treturn result+\" !!\"


"""
                },
            },
            "case_inputs_1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "name": "inputs"},
                "response_data": {"data": '{"args": [], "kwargs": {"name": "shore"}}'},
            },
            "case_error_1": {
                "status_code": 200,
                "path": {"dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd", "name": "error"},
                "response_data": {"data": ""},
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
                "response_data": {
                    "data": "{'lattice_metadata': {'executor': 'dask',\
                             'results_dir': '/home/arunmukesh/Desktop/files/results', \
                                'workflow_executor': 'dask', 'deps': {}, 'call_before': [], \
                                    'call_after': [], 'executor_data': {}, \
                                        'workflow_executor_data': {}}, 'dirty_nodes': []}"
                },
            },
        },
    }
