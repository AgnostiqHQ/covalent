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
    }
