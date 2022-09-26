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
                    + "/results/78525234-72ec-42dc-94a0-f4751707f9cd/node_0",
                    "name": "hello",
                    "status": "COMPLETED",
                    "started_at": "2022-09-23T15:31:11",
                    "ended_at": "2022-09-23T15:31:11",
                    "runtime": 0,
                    "description": "",
                },
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
                "response_data": {"data": '@ct.electron\ndef hello(): return "Hello "\n\n\n'},
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
                "response_data": {"data": '"Hello "'},
            },
            "case_value_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "value",
                },
                "response_data": {"data": None},
            },
            "case_stdout_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "stdout",
                },
                "response_data": {
                    "data": "DEBUG: update_electrons_data called on node 5\nDEBUG: update_electrons_data called on node 1\n"
                },
            },
            "case_deps_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "deps",
                },
                "response_data": {"data": None},
            },
            "case_call_before_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "call_before",
                },
                "response_data": {"data": ""},
            },
            "case_call_after_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "call_after",
                },
                "response_data": {"data": ""},
            },
            "case_error_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "error",
                },
                "response_data": {"data": ""},
            },
            "case_info_1": {
                "status_code": 200,
                "path": {
                    "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                    "electron_id": 0,
                    "name": "info",
                },
                "response_data": {"data": ""},
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
        },
    }
