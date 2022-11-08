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
                    "total_jobs": 2,
                    "total_jobs_running": 0,
                    "total_jobs_completed": 2,
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
                            "started_at": "2022-10-27T15:38:33",
                            "ended_at": "2022-10-27T15:38:43",
                            "status": "COMPLETED",
                            "updated_at": "2022-10-27T15:38:43",
                        },
                        {
                            "dispatch_id": VALID_DISPATCH_ID,
                            "lattice_name": "workflow",
                            "runtime": 0,
                            "total_electrons": 6,
                            "total_electrons_completed": 6,
                            "started_at": test_date,
                            "ended_at": test_date,
                            "status": "COMPLETED",
                            "updated_at": test_date,
                        },
                    ],
                    "total_count": 2,
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
                            "dispatch_id": VALID_DISPATCH_ID,
                            "lattice_name": "workflow",
                            "runtime": 0,
                            "total_electrons": 6,
                            "total_electrons_completed": 6,
                            "started_at": test_date,
                            "ended_at": test_date,
                            "status": "COMPLETED",
                            "updated_at": test_date,
                        }
                    ],
                    "total_count": 2,
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
                            "78525234-72ec-42dc-94a0-f4751707f9cd",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                            "f7eeb4ad-5262-49a5-aabc-cea10c6c1071",
                        ]
                    }
                },
                "response_data": {
                    "success_items": ["78525234-72ec-42dc-94a0-f4751707f9cd"],
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
                            "78525234-72ec-42dc-94a0-f4751707f9cd",
                            "78525234-72ec-42dc-94a0-f4751707f9c1",
                        ]
                    }
                },
                "response_data": {
                    "success_items": ["78525234-72ec-42dc-94a0-f4751707f9cd"],
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
                        "78525234-72ec-42dc-94a0-f4751707f9cd",
                        "a95d84ad-c441-446d-83ae-46380dcdf38e",
                        "89be0bcf-95dd-40a6-947e-6af6c56f147d",
                        "69dec597-79d9-4c99-96de-8d5f06f3d4dd",
                    ],
                    "failure_items": [],
                    "message": messages["success"],
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
            "case5": {"status_code": 422, "request_data": {"body": {"status_filter": "failed"}}},
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
