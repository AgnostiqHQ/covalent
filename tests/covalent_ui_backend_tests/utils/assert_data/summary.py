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

"Summary mock data"

from .config_data import VALID_DISPATCH_ID


def seed_summary_data():
    """Mock db sumary data"""
    messages = {
        "success": "Dispatch(es) have been deleted successfully!",
        "none": "No dispatches were deleted",
    }

    test_date = "2022-09-23T15:31:11"

    return {
        "test_overview": {
            "api_path": "/api/v1/dispatches/overview",
            "case1": {
                "status_code": 200,
                "response_data": {
                    "total_jobs": 3,
                    "total_jobs_running": 0,
                    "total_jobs_completed": 3,
                    "total_jobs_failed": 0,
                    "total_jobs_cancelled": 0,
                    "total_jobs_new_object": 0,
                    "latest_running_task_status": "COMPLETED",
                    "total_dispatcher_duration": 10000,
                },
            },
            "case2": {"status_code": 404},
        },
        "test_list": {
            "api_path": "/api/v1/dispatches/list",
            "case1": {
                "status_code": 200,
                "request_data": {
                    "query": {
                        "count": 10,
                        "sort_by": "runtime",
                        "sort_direction": "DESC",
                        "status_filter": "ALL",
                    }
                },
                "response_data": {
                    "items": [
                        {
                            "dispatch_id": "a95d84ad-c441-446d-83ae-46380dcdf38e",
                            "lattice_name": "workflow",
                            "runtime": 10000,
                            "total_electrons": 4,
                            "total_electrons_completed": 4,
                            "started_at": "2022-10-27T10:08:33.806638",
                            "ended_at": "2022-10-27T10:08:43.991108",
                            "status": "COMPLETED",
                            "updated_at": "2022-10-27T10:08:43.997619",
                        },
                        {
                            "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                            "lattice_name": "workflow",
                            "runtime": 0,
                            "total_electrons": 6,
                            "total_electrons_completed": 6,
                            "started_at": "2022-09-23T10:01:11.155428",
                            "ended_at": "2022-09-23T10:01:11.717064",
                            "status": "COMPLETED",
                            "updated_at": "2022-09-23T10:01:11.720140",
                        },
                        {
                            "dispatch_id": "e8fd09c9-1406-4686-9e77-c8d4d64a76ee",
                            "lattice_name": "workflow",
                            "runtime": 0,
                            "total_electrons": 2,
                            "total_electrons_completed": 2,
                            "started_at": "2023-08-10T10:08:55.420784",
                            "ended_at": "2023-08-10T10:08:55.902257",
                            "status": "COMPLETED",
                            "updated_at": "2023-08-10T10:08:55.946668",
                        },
                    ],
                    "total_count": 3,
                },
            },
            "case2": {
                "status_code": 200,
                "request_data": {
                    "query": {
                        "count": 1,
                        "sort_by": "status",
                        "sort_direction": "ASC",
                        "status_filter": "ALL",
                    }
                },
                "response_data": {
                    "items": [
                        {
                            "dispatch_id": "78525234-72ec-42dc-94a0-f4751707f9cd",
                            "lattice_name": "workflow",
                            "runtime": 0,
                            "total_electrons": 6,
                            "total_electrons_completed": 6,
                            "started_at": "2022-09-23T10:01:11.155428",
                            "ended_at": "2022-09-23T10:01:11.717064",
                            "status": "COMPLETED",
                            "updated_at": "2022-09-23T10:01:11.720140",
                        }
                    ],
                    "total_count": 3,
                },
            },
            "case3": {
                "status_code": 422,
                "request_data": {
                    "query": {
                        "count": 1,
                        "offset": -10,
                        "sort_by": "status",
                        "sort_direction": "ASC",
                        "search": "30",
                        "status_filter": "ALL",
                    }
                },
                "response_message": "ensure this value is greater than -1",
            },
            "case4": {
                "status_code": 422,
                "request_data": {
                    "query": {
                        "count": 0,
                        "sort_by": "status",
                        "sort_direction": "ASC",
                        "search": "30",
                        "status_filter": "ALL",
                    }
                },
                "response_data": {
                    "detail": [
                        {
                            "loc": ["query", "count"],
                            "msg": "ensure this value is greater than 0",
                            "type": "value_error.number.not_gt",
                            "ctx": {"limit_value": 0},
                        }
                    ]
                },
            },
        },
        "test_delete": {
            "api_path": "/api/v1/dispatches/delete",
            "case1": {
                "status_code": 200,
                "request_data": {"body": {"dispatches": [VALID_DISPATCH_ID]}},
                "response_data": {
                    "success_items": [VALID_DISPATCH_ID],
                    "failure_items": [],
                    "message": messages["success"],
                },
            },
            "case2": {
                "status_code": 200,
                "request_data": {"body": {"dispatches": ["f7eeb4ad-5262-49a5-aabc-cea10c6c1071"]}},
                "response_data": {
                    "success_items": [],
                    "failure_items": ["f7eeb4ad-5262-49a5-aabc-cea10c6c1071"],
                    "message": messages["none"],
                },
            },
            "case3": {
                "status_code": 200,
                "request_data": {
                    "body": {
                        "dispatches": [
                            "a95d84ad-c441-446d-83ae-46380dcdf38e",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                        ]
                    }
                },
                "response_data": {
                    "success_items": ["a95d84ad-c441-446d-83ae-46380dcdf38e"],
                    "failure_items": [
                        "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                        "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                        "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                    ],
                    "message": "Some of the dispatches could not be deleted",
                },
            },
            "case4": {
                "status_code": 422,
                "request_data": {
                    "body": {
                        "dispatches": [
                            "05669868aa",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                        ]
                    }
                },
                "response_message": "value is not a valid uuid",
            },
            "case5": {
                "status_code": 200,
                "request_data": {"body": {"dispatches": []}},
                "response_data": {
                    "success_items": [],
                    "failure_items": [],
                    "message": messages["none"],
                },
            },
            "case6": {
                "status_code": 200,
                "request_data": {"body": {"dispatches": None}},
                "response_data": {
                    "success_items": [],
                    "failure_items": [],
                    "message": messages["none"],
                },
            },
            "case7": {
                "status_code": 200,
                "request_data": {"body": {"dispatches": ["78525234-72ec-42dc-94a0-f4751707f9cd"]}},
                "response_data": {
                    "success_items": [],
                    "failure_items": ["78525234-72ec-42dc-94a0-f4751707f9cd"],
                    "message": messages["none"],
                },
            },
            "case8": {
                "status_code": 200,
                "request_data": {
                    "body": {
                        "dispatches": [
                            "89be0bcf-95dd-40a6-947e-6af6c56f147d",
                            "78525234-72ec-42dc-94a0-f4751707f9c1",
                        ]
                    }
                },
                "response_data": {
                    "success_items": ["89be0bcf-95dd-40a6-947e-6af6c56f147d"],
                    "failure_items": ["78525234-72ec-42dc-94a0-f4751707f9c1"],
                    "message": "Some of the dispatches could not be deleted",
                },
            },
        },
        "test_delete_all": {
            "api_path": "/api/v1/dispatches/delete-all",
            "case1": {
                "status_code": 200,
                "request_data": {"body": {"status_filter": "ALL", "search_string": ""}},
                "response_data": {
                    "success_items": [
                        "69dec597-79d9-4c99-96de-8d5f06f3d4dd",
                        "e8fd09c9-1406-4686-9e77-c8d4d64a76ee",
                    ],
                    "failure_items": [],
                    "message": "Dispatch(es) have been deleted successfully!",
                },
            },
            "case2": {
                "status_code": 200,
                "request_data": {"body": {"status_filter": "COMPLETED", "search_string": ""}},
                "response_data": {
                    "success_items": ["78525234-72ec-42dc-94a0-f4751707f9cd"],
                    "failure_items": [],
                    "message": messages["success"],
                },
            },
            "case3": {
                "status_code": 200,
                "request_data": {"body": {"status_filter": "ALL", "search_string": "random"}},
                "response_data": {
                    "success_items": [],
                    "failure_items": [],
                    "message": messages["none"],
                },
            },
            "case4": {
                "status_code": 200,
                "request_data": {"body": {"status_filter": "FAILED", "search_string": "random"}},
                "response_data": {
                    "success_items": [],
                    "failure_items": [],
                    "message": messages["none"],
                },
            },
            "case5": {
                "status_code": 422,
                "request_data": {"body": {"status_filter": "failed"}},
                "response_message": "value is not a valid enumeration member; permitted: 'ALL', 'NEW_OBJECT', 'COMPLETED', 'POSTPROCESSING', 'PENDING_POSTPROCESSING', 'POSTPROCESSING_FAILED', 'FAILED', 'RUNNING', 'CANCELLED'",
            },
            "case6": {
                "status_code": 200,
                "request_data": {"body": {"status_filter": "FAILED", "search_string": "random"}},
                "response_data": {
                    "success_items": [],
                    "failure_items": [],
                    "message": messages["none"],
                },
            },
        },
    }
