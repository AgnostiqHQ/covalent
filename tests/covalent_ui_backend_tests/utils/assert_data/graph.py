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

"""Graph mock data"""

import datetime

from .config_data import INVALID_DISPATCH_ID, VALID_DISPATCH_ID


def seed_graph_data():
    """Mock db assert graph data"""

    return {
        "test_graph": {
            "api_path": "api/v1/dispatches/{}/graph",
            "case_test_get_graph": {
                "status_code": 200,
                "path": {"dispatch_id": VALID_DISPATCH_ID},
                "response_data": {
                    "dispatch_id": VALID_DISPATCH_ID,
                    "graph": {
                        "nodes": [
                            {
                                "id": 1,
                                "name": "hello",
                                "node_id": 0,
                                "started_at": "2022-09-23 10:01:11.168972",
                                "completed_at": "2022-09-23 10:01:11.483405",
                                "status": "COMPLETED",
                                "type": "function",
                                "executor_label": "dask",
                                "sublattice_dispatch_id": None,
                            },
                            {
                                "id": 2,
                                "name": "moniker",
                                "node_id": 1,
                                "started_at": "2022-09-23 10:01:11.264347",
                                "completed_at": "2022-09-23 10:01:11.520838",
                                "status": "COMPLETED",
                                "type": "function",
                                "executor_label": "dask",
                                "sublattice_dispatch_id": None,
                            },
                            {
                                "id": 3,
                                "name": ":parameter:shore",
                                "node_id": 2,
                                "started_at": "2022-09-23 10:01:11.194417",
                                "completed_at": "2022-09-23 10:01:11.194419",
                                "status": "COMPLETED",
                                "type": "parameter",
                                "executor_label": "dask",
                                "sublattice_dispatch_id": None,
                            },
                            {
                                "id": 4,
                                "name": "join",
                                "node_id": 3,
                                "started_at": "2022-09-23 10:01:11.553084",
                                "completed_at": "2022-09-23 10:01:11.588248",
                                "status": "COMPLETED",
                                "type": "function",
                                "executor_label": "dask",
                                "sublattice_dispatch_id": None,
                            },
                            {
                                "id": 5,
                                "name": "join_+_ !!",
                                "node_id": 4,
                                "started_at": "2022-09-23 10:01:11.611520",
                                "completed_at": "2022-09-23 10:01:11.640049",
                                "status": "COMPLETED",
                                "type": "function",
                                "executor_label": "dask",
                                "sublattice_dispatch_id": None,
                            },
                            {
                                "id": 6,
                                "name": ":parameter: !!",
                                "node_id": 5,
                                "started_at": "2022-09-23 10:01:11.226984",
                                "completed_at": "2022-09-23 10:01:11.226986",
                                "status": "COMPLETED",
                                "type": "parameter",
                                "executor_label": "dask",
                                "sublattice_dispatch_id": None,
                            },
                        ],
                        "links": [
                            {
                                "edge_name": "arg[0]",
                                "parameter_type": "arg",
                                "target": 4,
                                "source": 1,
                                "arg_index": 0,
                            },
                            {
                                "edge_name": "arg[1]",
                                "parameter_type": "arg",
                                "target": 4,
                                "source": 2,
                                "arg_index": 1,
                            },
                            {
                                "edge_name": "name",
                                "parameter_type": "arg",
                                "target": 2,
                                "source": 3,
                                "arg_index": 0,
                            },
                            {
                                "edge_name": "arg_1",
                                "parameter_type": "kwarg",
                                "target": 5,
                                "source": 4,
                                "arg_index": None,
                            },
                            {
                                "edge_name": "arg_2",
                                "parameter_type": "kwarg",
                                "target": 5,
                                "source": 6,
                                "arg_index": None,
                            },
                        ],
                    },
                },
            },
            "case_test_graph_invalid_dispatch_id": {
                "status_code": 400,
                "path": {"dispatch_id": INVALID_DISPATCH_ID},
                "response_data": {
                    "detail": [
                        {
                            "loc": ["path", "dispatch_id"],
                            "msg": f"Dispatch ID {INVALID_DISPATCH_ID} does not exist",
                            "type": None,
                        }
                    ]
                },
            },
            "case_func_get_nodes": {
                "response_data": [
                    (
                        1,
                        "hello",
                        0,
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 168972),
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 483405),
                        "COMPLETED",
                        "function",
                        "dask",
                    ),
                    (
                        2,
                        "moniker",
                        1,
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 264347),
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 520838),
                        "COMPLETED",
                        "function",
                        "dask",
                    ),
                    (
                        3,
                        ":parameter:shore",
                        2,
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 194417),
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 194419),
                        "COMPLETED",
                        "parameter",
                        "dask",
                    ),
                    (
                        4,
                        "join",
                        3,
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 553084),
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 588248),
                        "COMPLETED",
                        "function",
                        "dask",
                    ),
                    (
                        5,
                        "join_+_ !!",
                        4,
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 611520),
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 640049),
                        "COMPLETED",
                        "function",
                        "dask",
                    ),
                    (
                        6,
                        ":parameter: !!",
                        5,
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 226984),
                        datetime.datetime(2022, 9, 23, 10, 1, 11, 226986),
                        "COMPLETED",
                        "parameter",
                        "dask",
                    ),
                ]
            },
            "case_func_get_links": {
                "response_data": [
                    ("4", "arg", 4, 4, 0),
                    ("4", "arg", 4, 4, 1),
                    ("2", "arg", 2, 2, 0),
                    ("5", "kwarg", 5, 5, None),
                    ("5", "kwarg", 5, 5, None),
                ]
            },
        }
    }
