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

"Logs mock data"
import copy

from .config_data import LOG_FORMAT, LOG_LEVEL, LOG_TO_FILE


def seed_logs_data():
    """Mock db logs data"""
    messages = {
        "startup": "Application startup complete.",
        "wait": "Waiting for application startup.",
        "started": "Started server process [41482]",
    }
    access = "uvicorn.access"
    error = "uvicorn.error"

    log = LOG_LEVEL if LOG_TO_FILE else None

    handler_format = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": LOG_FORMAT,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": LOG_FORMAT,
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            error: {"level": "INFO", "handlers": ["default"], "propogate": False},
            access: {"level": "INFO", "handlers": ["access"], "propagate": "no"},
        },
    }
    handler_format_1 = copy.deepcopy(handler_format)
    handler_format_2 = copy.deepcopy(handler_format)
    handler_format_1["loggers"][error]["level"] = log
    handler_format_1["loggers"][access]["level"] = log
    handler_format_2["loggers"][error]["level"] = None
    handler_format_2["loggers"][access]["level"] = None
    return {
        "test_logs": {
            "api_path": "/api/v1/logs/",
            "case1": {
                "status_code": 200,
                "response_data": {
                    "items": [
                        {
                            "log_date": "2022-09-23 07:43:59.752000",
                            "status": "INFO",
                            "message": " Started server process [41482]\n",
                        },
                        {
                            "log_date": "2022-09-23 07:43:59.753000",
                            "status": "INFO",
                            "message": " Waiting for application startup.\n",
                        },
                        {
                            "log_date": "2022-09-23 07:44:01.753000",
                            "status": "INFO",
                            "message": " Application startup complete.\n",
                        },
                        {
                            "log_date": "2022-09-26 07:44:16.411000",
                            "status": "INFO",
                            "message": ' 127.0.0.1:47378 - "GET /docs HTTP/1.1" 200\n',
                        },
                        {
                            "log_date": "2022-09-26 07:45:27.907000",
                            "status": "INFO",
                            "message": ' 127.0.0.1:47378 - "GET /openapi.json HTTP/1.1" 200',
                        },
                    ],
                    "total_count": 5,
                },
            },
            "case2": {
                "status_code": 200,
                "request_data": {
                    "query": {
                        "count": 2,
                        "offset": 0,
                        "search": "",
                        "sort_by": "log_date",
                        "sort_direction": "DESC",
                    }
                },
                "response_data": {
                    "items": [
                        {
                            "log_date": "2022-09-26 07:41:42.907000",
                            "status": "INFO",
                            "message": '127.0.0.1:47378 - "GET /openapi.json HTTP/1.1" 200\nconnection Closed\n\nKilled',
                        },
                        {
                            "log_date": "2022-09-26 07:42:44.907000",
                            "status": "INFO",
                            "message": "WebSocket - connection open",
                        },
                    ],
                    "total_count": 7,
                },
            },
            "case3": {
                "status_code": 200,
                "request_data": {
                    "query": {
                        "count": 10,
                        "offset": 4,
                        "search": "",
                        "sort_by": "log_date",
                        "sort_direction": "DESC",
                    }
                },
                "response_data": {
                    "items": [
                        {
                            "log_date": "2022-09-23 07:43:59.753000",
                            "status": "INFO",
                            "message": messages["wait"],
                        },
                        {
                            "log_date": "2022-09-23 07:45:23.753000",
                            "status": "INFO",
                            "message": messages["startup"],
                        },
                        {
                            "log_date": "2022-09-23 07:45:47.752000",
                            "status": "INFO",
                            "message": messages["started"],
                        },
                    ],
                    "total_count": 7,
                },
            },
            "case4": {
                "status_code": 200,
                "request_data": {
                    "query": {
                        "count": 5,
                        "offset": 0,
                        "search": "favicon",
                        "sort_by": "log_date",
                        "sort_direction": "DESC",
                    }
                },
                "response_data": {
                    "items": [
                        {
                            "log_date": "2022-09-26 07:41:42.907000",
                            "status": "INFO",
                            "message": '127.0.0.1:47378 - "GET /favicon.ico HTTP/1.1" 404',
                        }
                    ],
                    "total_count": 1,
                },
            },
            "case1_1": {
                "status_code": 200,
                "request_data": {
                    "query": {
                        "count": 5,
                        "offset": 0,
                        "search": "favicon",
                        "sort_by": "log_date",
                        "sort_direction": "DESC",
                    }
                },
                "response_data": {
                    "items": [
                        {"log_date": None, "status": "INFO", "message": "Killed\n"},
                        {
                            "log_date": "2022-09-23 03:01:52.752000",
                            "status": "INFO",
                            "message": " Started server process [41482]\n",
                        },
                        {
                            "log_date": "2022-09-23 03:11:11.753000",
                            "status": "INFO",
                            "message": " Waiting for application startup.\n",
                        },
                        {
                            "log_date": "2022-09-23 03:43:57.753000",
                            "status": "INFO",
                            "message": " Application startup complete.\n",
                        },
                        {
                            "log_date": "2022-09-26 05:14:33.411000",
                            "status": "INFO",
                            "message": ' 127.0.0.1:47378 - "GET /docs HTTP/1.1" 200\n',
                        },
                        {
                            "log_date": "2022-09-26 05:28:54.907000",
                            "status": "INFO",
                            "message": ' 127.0.0.1:47378 - "GET /openapi.json HTTP/1.1" 200\n\nconnection Closed\n',
                        },
                        {
                            "log_date": "2022-09-26 06:00:42.907000",
                            "status": "INFO",
                            "message": " WebSocket - connection open\n",
                        },
                        {
                            "log_date": "2022-09-26 06:36:46.907000",
                            "status": "INFO",
                            "message": ' 127.0.0.1:47378 - "GET /favicon.ico HTTP/1.1" 404\n\nConnection Closed\n\nkilled',
                        },
                    ],
                    "total_count": 8,
                },
            },
            "case5": {"status_code": 200, "response_data": {"items": [], "total_count": 0}},
        },
        "test_download_logs": {
            "api_path": "/api/v1/logs/download",
            "case1": {"status_code": 200},
            "case_functional_1": {"response_type": "Response"},
        },
        "test_logs_handler": {
            "handler_format1": handler_format_1,
            "handler_format2": handler_format_2,
        },
    }
