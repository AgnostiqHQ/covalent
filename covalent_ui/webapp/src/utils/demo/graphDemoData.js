/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */

const graphDemoData = [];

// Dispatch 2537c3b0-c150-441b-81c6-844e3fd88ef3
graphDemoData["2537c3b0-c150-441b-81c6-844e3fd88ef3"] = {
    "dispatch_id": "2537c3b0-c150-441b-81c6-844e3fd88ef3",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "construct_n_molecule",
                "node_id": 0,
                "started_at": "2022-10-11 12:42:03.373695",
                "completed_at": "2022-10-11 12:42:03.966670",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1.1",
                "node_id": 1,
                "started_at": "2022-10-11 12:42:02.847567",
                "completed_at": "2022-10-11 12:42:02.847574",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": "compute_system_energy",
                "node_id": 2,
                "started_at": "2022-10-11 12:42:04.239834",
                "completed_at": "2022-10-11 12:42:04.665718",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": "construct_cu_slab",
                "node_id": 3,
                "started_at": "2022-10-11 12:42:03.670400",
                "completed_at": "2022-10-11 12:42:04.931221",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": ":parameter:(4, 4, 2)",
                "node_id": 4,
                "started_at": "2022-10-11 12:42:02.895675",
                "completed_at": "2022-10-11 12:42:02.895679",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": ":parameter:10.0",
                "node_id": 5,
                "started_at": "2022-10-11 12:42:02.930323",
                "completed_at": "2022-10-11 12:42:02.930329",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 6,
                "name": "compute_system_energy",
                "node_id": 6,
                "started_at": "2022-10-11 12:42:04.978366",
                "completed_at": "2022-10-11 12:42:05.232120",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 7,
                "name": "get_relaxed_slab",
                "node_id": 7,
                "started_at": "2022-10-11 12:42:05.014881",
                "completed_at": "2022-10-11 12:42:15.456735",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 8,
                "name": ":parameter:3",
                "node_id": 8,
                "started_at": "2022-10-11 12:42:03.204774",
                "completed_at": "2022-10-11 12:42:03.204800",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 9,
                "name": "compute_system_energy",
                "node_id": 9,
                "started_at": "2022-10-11 12:42:15.476646",
                "completed_at": "2022-10-11 12:42:15.766368",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 10,
                "name": "compute_system_energy_+_compute_system_energy",
                "node_id": 10,
                "started_at": "2022-10-11 12:42:05.307984",
                "completed_at": "2022-10-11 12:42:05.512133",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 11,
                "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
                "node_id": 11,
                "started_at": "2022-10-11 12:42:15.789210",
                "completed_at": "2022-10-11 12:42:15.824352",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 2,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "molecule",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "d",
                "parameter_type": "kwarg",
                "target": 0,
                "source": 1,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 2,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "slab",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "unit_cell",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 4,
                "arg_index": null
            },
            {
                "edge_name": "vacuum",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 5,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 6,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 9,
                "source": 7,
                "arg_index": null
            },
            {
                "edge_name": "height",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 8,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 9,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 10,
                "arg_index": null
            }
        ]
    }
}

// Dispatch eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a
graphDemoData["eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a"] = {
    "dispatch_id": "eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "construct_n_molecule",
                "node_id": 0,
                "started_at": "2022-10-11 12:42:03.373695",
                "completed_at": "2022-10-11 12:42:03.966670",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1.1",
                "node_id": 1,
                "started_at": "2022-10-11 12:42:02.847567",
                "completed_at": "2022-10-11 12:42:02.847574",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": "compute_system_energy",
                "node_id": 2,
                "started_at": "2022-10-11 12:42:04.239834",
                "completed_at": "2022-10-11 12:42:04.665718",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": "construct_cu_slab",
                "node_id": 3,
                "started_at": "2022-10-11 12:42:03.670400",
                "completed_at": "2022-10-11 12:42:04.931221",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": ":parameter:(4, 4, 2)",
                "node_id": 4,
                "started_at": "2022-10-11 12:42:02.895675",
                "completed_at": "2022-10-11 12:42:02.895679",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": ":parameter:10.0",
                "node_id": 5,
                "started_at": "2022-10-11 12:42:02.930323",
                "completed_at": "2022-10-11 12:42:02.930329",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 6,
                "name": "compute_system_energy",
                "node_id": 6,
                "started_at": "2022-10-11 12:42:04.978366",
                "completed_at": "2022-10-11 12:42:05.232120",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 7,
                "name": "get_relaxed_slab",
                "node_id": 7,
                "started_at": "2022-10-11 12:42:05.014881",
                "completed_at": "2022-10-11 12:42:15.456735",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 8,
                "name": ":parameter:3",
                "node_id": 8,
                "started_at": "2022-10-11 12:42:03.204774",
                "completed_at": "2022-10-11 12:42:03.204800",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 9,
                "name": "compute_system_energy",
                "node_id": 9,
                "started_at": "2022-10-11 12:42:15.476646",
                "completed_at": "2022-10-11 12:42:15.766368",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 10,
                "name": "compute_system_energy_+_compute_system_energy",
                "node_id": 10,
                "started_at": "2022-10-11 12:42:05.307984",
                "completed_at": "2022-10-11 12:42:05.512133",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 11,
                "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
                "node_id": 11,
                "started_at": "2022-10-11 12:42:15.789210",
                "completed_at": "2022-10-11 12:42:15.824352",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 2,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "molecule",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "d",
                "parameter_type": "kwarg",
                "target": 0,
                "source": 1,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 2,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "slab",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "unit_cell",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 4,
                "arg_index": null
            },
            {
                "edge_name": "vacuum",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 5,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 6,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 9,
                "source": 7,
                "arg_index": null
            },
            {
                "edge_name": "height",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 8,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 9,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 10,
                "arg_index": null
            }
        ]
    }
}

// Dispatch fcd385e2-7881-4bcd-862c-2ac99706d2f9
graphDemoData["fcd385e2-7881-4bcd-862c-2ac99706d2f9"] = {
    "dispatch_id": "fcd385e2-7881-4bcd-862c-2ac99706d2f9",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "construct_n_molecule",
                "node_id": 0,
                "started_at": "2022-10-11 12:42:03.373695",
                "completed_at": "2022-10-11 12:42:03.966670",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1.1",
                "node_id": 1,
                "started_at": "2022-10-11 12:42:02.847567",
                "completed_at": "2022-10-11 12:42:02.847574",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": "compute_system_energy",
                "node_id": 2,
                "started_at": "2022-10-11 12:42:04.239834",
                "completed_at": "2022-10-11 12:42:04.665718",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": "construct_cu_slab",
                "node_id": 3,
                "started_at": "2022-10-11 12:42:03.670400",
                "completed_at": "2022-10-11 12:42:04.931221",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": ":parameter:(4, 4, 2)",
                "node_id": 4,
                "started_at": "2022-10-11 12:42:02.895675",
                "completed_at": "2022-10-11 12:42:02.895679",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": ":parameter:10.0",
                "node_id": 5,
                "started_at": "2022-10-11 12:42:02.930323",
                "completed_at": "2022-10-11 12:42:02.930329",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 6,
                "name": "compute_system_energy",
                "node_id": 6,
                "started_at": "2022-10-11 12:42:04.978366",
                "completed_at": "2022-10-11 12:42:05.232120",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 7,
                "name": "get_relaxed_slab",
                "node_id": 7,
                "started_at": "2022-10-11 12:42:05.014881",
                "completed_at": "2022-10-11 12:42:15.456735",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 8,
                "name": ":parameter:3",
                "node_id": 8,
                "started_at": "2022-10-11 12:42:03.204774",
                "completed_at": "2022-10-11 12:42:03.204800",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 9,
                "name": "compute_system_energy",
                "node_id": 9,
                "started_at": "2022-10-11 12:42:15.476646",
                "completed_at": "2022-10-11 12:42:15.766368",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 10,
                "name": "compute_system_energy_+_compute_system_energy",
                "node_id": 10,
                "started_at": "2022-10-11 12:42:05.307984",
                "completed_at": "2022-10-11 12:42:05.512133",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 11,
                "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
                "node_id": 11,
                "started_at": "2022-10-11 12:42:15.789210",
                "completed_at": "2022-10-11 12:42:15.824352",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 2,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "molecule",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "d",
                "parameter_type": "kwarg",
                "target": 0,
                "source": 1,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 2,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "slab",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "unit_cell",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 4,
                "arg_index": null
            },
            {
                "edge_name": "vacuum",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 5,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 6,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 9,
                "source": 7,
                "arg_index": null
            },
            {
                "edge_name": "height",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 8,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 9,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 10,
                "arg_index": null
            }
        ]
    }
}

// Dispatch b199afa5-301f-47d8-a8dc-fd78e1f5d08a
graphDemoData["b199afa5-301f-47d8-a8dc-fd78e1f5d08a"] = {
    "dispatch_id": "b199afa5-301f-47d8-a8dc-fd78e1f5d08a",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "construct_n_molecule",
                "node_id": 0,
                "started_at": "2022-10-11 12:42:03.373695",
                "completed_at": "2022-10-11 12:42:03.966670",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1.1",
                "node_id": 1,
                "started_at": "2022-10-11 12:42:02.847567",
                "completed_at": "2022-10-11 12:42:02.847574",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": "compute_system_energy",
                "node_id": 2,
                "started_at": "2022-10-11 12:42:04.239834",
                "completed_at": "2022-10-11 12:42:04.665718",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": "construct_cu_slab",
                "node_id": 3,
                "started_at": "2022-10-11 12:42:03.670400",
                "completed_at": "2022-10-11 12:42:04.931221",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": ":parameter:(4, 4, 2)",
                "node_id": 4,
                "started_at": "2022-10-11 12:42:02.895675",
                "completed_at": "2022-10-11 12:42:02.895679",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": ":parameter:10.0",
                "node_id": 5,
                "started_at": "2022-10-11 12:42:02.930323",
                "completed_at": "2022-10-11 12:42:02.930329",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 6,
                "name": "compute_system_energy",
                "node_id": 6,
                "started_at": "2022-10-11 12:42:04.978366",
                "completed_at": "2022-10-11 12:42:05.232120",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 7,
                "name": "get_relaxed_slab",
                "node_id": 7,
                "started_at": "2022-10-11 12:42:05.014881",
                "completed_at": "2022-10-11 12:42:15.456735",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 8,
                "name": ":parameter:3",
                "node_id": 8,
                "started_at": "2022-10-11 12:42:03.204774",
                "completed_at": "2022-10-11 12:42:03.204800",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 9,
                "name": "compute_system_energy",
                "node_id": 9,
                "started_at": "2022-10-11 12:42:15.476646",
                "completed_at": "2022-10-11 12:42:15.766368",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 10,
                "name": "compute_system_energy_+_compute_system_energy",
                "node_id": 10,
                "started_at": "2022-10-11 12:42:05.307984",
                "completed_at": "2022-10-11 12:42:05.512133",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 11,
                "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
                "node_id": 11,
                "started_at": "2022-10-11 12:42:15.789210",
                "completed_at": "2022-10-11 12:42:15.824352",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 2,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "molecule",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "d",
                "parameter_type": "kwarg",
                "target": 0,
                "source": 1,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 2,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "slab",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "unit_cell",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 4,
                "arg_index": null
            },
            {
                "edge_name": "vacuum",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 5,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 6,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 9,
                "source": 7,
                "arg_index": null
            },
            {
                "edge_name": "height",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 8,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 9,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 10,
                "arg_index": null
            }
        ]
    }
}

// Dispatch df4601e7-7658-4a14-a860-f91a35a1b453
graphDemoData["df4601e7-7658-4a14-a860-f91a35a1b453"] = {
    "dispatch_id": "df4601e7-7658-4a14-a860-f91a35a1b453",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "construct_n_molecule",
                "node_id": 0,
                "started_at": "2022-10-11 12:42:03.373695",
                "completed_at": "2022-10-11 12:42:03.966670",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1.1",
                "node_id": 1,
                "started_at": "2022-10-11 12:42:02.847567",
                "completed_at": "2022-10-11 12:42:02.847574",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": "compute_system_energy",
                "node_id": 2,
                "started_at": "2022-10-11 12:42:04.239834",
                "completed_at": "2022-10-11 12:42:04.665718",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": "construct_cu_slab",
                "node_id": 3,
                "started_at": "2022-10-11 12:42:03.670400",
                "completed_at": "2022-10-11 12:42:04.931221",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": ":parameter:(4, 4, 2)",
                "node_id": 4,
                "started_at": "2022-10-11 12:42:02.895675",
                "completed_at": "2022-10-11 12:42:02.895679",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": ":parameter:10.0",
                "node_id": 5,
                "started_at": "2022-10-11 12:42:02.930323",
                "completed_at": "2022-10-11 12:42:02.930329",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 6,
                "name": "compute_system_energy",
                "node_id": 6,
                "started_at": "2022-10-11 12:42:04.978366",
                "completed_at": "2022-10-11 12:42:05.232120",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 7,
                "name": "get_relaxed_slab",
                "node_id": 7,
                "started_at": "2022-10-11 12:42:05.014881",
                "completed_at": "2022-10-11 12:42:15.456735",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 8,
                "name": ":parameter:3",
                "node_id": 8,
                "started_at": "2022-10-11 12:42:03.204774",
                "completed_at": "2022-10-11 12:42:03.204800",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 9,
                "name": "compute_system_energy",
                "node_id": 9,
                "started_at": "2022-10-11 12:42:15.476646",
                "completed_at": "2022-10-11 12:42:15.766368",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 10,
                "name": "compute_system_energy_+_compute_system_energy",
                "node_id": 10,
                "started_at": "2022-10-11 12:42:05.307984",
                "completed_at": "2022-10-11 12:42:05.512133",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 11,
                "name": "compute_system_energy_+_compute_system_energy_-_compute_system_energy",
                "node_id": 11,
                "started_at": "2022-10-11 12:42:15.789210",
                "completed_at": "2022-10-11 12:42:15.824352",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 2,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "molecule",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 0,
                "arg_index": null
            },
            {
                "edge_name": "d",
                "parameter_type": "kwarg",
                "target": 0,
                "source": 1,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 2,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "slab",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 3,
                "arg_index": null
            },
            {
                "edge_name": "unit_cell",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 4,
                "arg_index": null
            },
            {
                "edge_name": "vacuum",
                "parameter_type": "kwarg",
                "target": 3,
                "source": 5,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 10,
                "source": 6,
                "arg_index": null
            },
            {
                "edge_name": "system",
                "parameter_type": "kwarg",
                "target": 9,
                "source": 7,
                "arg_index": null
            },
            {
                "edge_name": "height",
                "parameter_type": "kwarg",
                "target": 7,
                "source": 8,
                "arg_index": null
            },
            {
                "edge_name": "arg_2",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 9,
                "arg_index": null
            },
            {
                "edge_name": "arg_1",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 10,
                "arg_index": null
            }
        ]
    }
}

//   Dispatch ba3c238c-cb92-48e8-b7b2-debeebe2e81a

graphDemoData["ba3c238c-cb92-48e8-b7b2-debeebe2e81a"] = {
    "dispatch_id": "ba3c238c-cb92-48e8-b7b2-debeebe2e81a",
    "graph": {
        nodes: [
            {
                name: 'get_RA',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_RA(target_list):\n    RA = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        RA.append(\n            star_info[star_info.index("<TR><TD>") + 8 : star_info.index("</TD><TD>")]\n        )\n    RA_degs = []\n    for source in RA:\n        hour = float(source.split(" ")[0])\n        minute = float(source.split(" ")[1])\n        second = float(source.split(" ")[2])\n        RA_degs.append(((hour + minute / 60 + second / 3600) * 15))\n    return RA_degs\n\n\n',
                id: 0,
                doc: null,
executor_label:'dask',
                status: 'FAILED'
            },
            {
                name: 'electron list',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string: '# to_electron_collection was not inspectable\n\n',
                id: 1,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:sirius',
                kwargs: {
                    target_list: 'sirius',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 2,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:trappist-1',
                kwargs: {
                    target_list: 'trappist-1',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 3,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'get_dec',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_dec(target_list):\n    dec = []\n    for target_name in target_list:\n        response = requests.get(\n            "http://simbad.u-strasbg.fr/simbad/sim-id?output.format=votable&Ident=%s&output.params=ra,dec"\n            % target_name\n        )\n        star_info = response.text\n        dec.append(\n            star_info[star_info.index("</TD><TD>") + 9 : star_info.index("</TD></TR>")]\n        )\n    dec_degs = []\n    for source in dec:\n        degree = float(source.split(" ")[0])\n        arcmin = float(source.split(" ")[1])\n        arcsec = float(source.split(" ")[2])\n        if degree < 0:\n            dec_degs.append(degree - arcmin / 60 - arcsec / 3600)\n        else:\n            dec_degs.append(degree + arcmin / 60 + arcsec / 3600)\n    return dec_degs\n\n\n',
                id: 4,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'electron list',
                kwargs: {
                    target_list: "['sirius', 'trappist-1']",
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string: '# to_electron_collection was not inspectable\n\n',
                id: 5,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:sirius',
                kwargs: {
                    target_list: 'sirius',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 6,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:trappist-1',
                kwargs: {
                    target_list: 'trappist-1',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 7,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'convert_to_utc',
                kwargs: {
                    time_zone: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef convert_to_utc(time_zone):\n    start_time = 0\n    end_time = 24.016\n    now = datetime.now(pytz.timezone(time_zone))\n    offset = now.utcoffset().total_seconds() / 60 / 60\n    utc_timerange = np.arange(start_time - offset, end_time - offset, 0.016)\n    return utc_timerange\n\n\n',
                id: 8,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:America/Los_Angeles',
                kwargs: {
                    time_zone: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 9,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'days_since_J2000',
                kwargs: {
                    region: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef days_since_J2000(region):\n    f_date = date(2000, 1, 1)\n    year = get_date(time_zone=region)[0]\n    month = get_date(time_zone=region)[1]\n    day = get_date(time_zone=region)[2]\n    l_date = date(year, month, day)\n    delta = l_date - f_date\n    return delta.days\n\n\n',
                id: 10,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:America/Los_Angeles',
                kwargs: {
                    region: 'America/Los_Angeles',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 11,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'local_sidereal_time',
                kwargs: {
                    d: '<covalent._workflow.electron.Electron object at 0x7f839d9c3550>',
                    long: '-123.1207',
                    T: '<covalent._workflow.electron.Electron object at 0x7f839d9a8100>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef local_sidereal_time(d, long, T):\n    LST = 100.46 + 0.985647 * (d + T / 24) + long + 15 * T\n    return LST\n\n\n',
                id: 12,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: ':parameter:-123.1207',
                kwargs: {
                    long: '-123.1207',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 13,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'hour_angle',
                kwargs: {
                    LST: '<covalent._workflow.electron.Electron object at 0x7f839d9c3eb0>',
                    RA: '<covalent._workflow.electron.Electron object at 0x7f839da53d00>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef hour_angle(LST, RA):\n    LST_list = []\n    for source in RA:\n        LST_list.append(np.asarray([value - source for value in LST]))\n    return LST_list\n\n\n',
                id: 14,
                doc: null,
executor_label:'dask',
                status: 'PENDING'
            },
            {
                name: 'altitude_of_target',
                kwargs: {
                    dec: '<covalent._workflow.electron.Electron object at 0x7f839d997460>',
                    lat: '49.2827',
                    ha: '<covalent._workflow.electron.Electron object at 0x7f839d9c3b80>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef altitude_of_target(dec, lat, ha):\n    alt_list = []\n    lat = lat * 0.0174533\n    for i in range(len(dec)):\n        dec_i = dec[i] * 0.0174533\n        ha_i = ha[i] * 0.0174533\n        alt = np.arcsin(\n            np.sin(dec_i) * np.sin(lat) + np.cos(dec_i) * np.cos(lat) * np.cos(ha_i)\n        )\n        alt_list.append(alt * 57.2958)\n    return alt_list\n\n\n',
                id: 15,
                doc: null,
executor_label:'dask',
                status: 'PENDING'
            },
            {
                name: ':parameter:49.2827',
                kwargs: {
                    lat: '49.2827',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 16,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
            {
                name: 'get_azimuth',
                kwargs: {
                    dec: '<covalent._workflow.electron.Electron object at 0x7f839d997460>',
                    lat: '49.2827',
                    ha: '<covalent._workflow.electron.Electron object at 0x7f839d9c3b80>',
                    alt: '<covalent._workflow.electron.Electron object at 0x7f839d9b5610>',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                function_string:
                    '# @ct.electron\ndef get_azimuth(dec, lat, ha, alt):\n    az_list = []\n    lat = round(lat * 0.0174533, 2)\n    for i in range(len(dec)):\n        azimuth = []\n        dec_i = round(dec[i] * 0.0174533, 2)\n        ha_i = ha[i] * 0.0174533\n        alt_i = alt[i] * 0.0174533\n        a = np.arccos(\n            (np.sin(dec_i) - np.sin(alt_i) * np.sin(lat))\n            / (np.cos(alt_i) * np.cos(lat))\n        )\n        for q in range(len(ha_i)):\n            if np.sin(ha_i[q]) < 0:\n                azimuth.append(a[q] * 57.2958)\n            else:\n                azimuth.append(360 - (a[q] * 57.2958))\n        az_list.append(np.array(azimuth))\n    return az_list\n\n\n',
                id: 17,
                doc: null,
executor_label:'dask',
                status: 'PENDING'
            },
            {
                name: ':parameter:49.2827',
                kwargs: {
                    lat: '49.2827',
                },
                metadata: {
                    backend: 'local',
                    executor: {
                        log_stdout: 'stdout.log',
                        log_stderr: 'stderr.log',
                        conda_env: '',
                        cache_dir: '/tmp/covalent',
                        current_env_on_conda_fail: 'False',
                        current_env: '',
                    },
                },
                id: 18,
                doc: null,
executor_label:'dask',
                status: 'COMPLETED'
            },
        ],
        links: [
            {
                variable: 'RA',
                source: 0,
                target: 14,
            },
            {
                variable: 'target_list',
                source: 1,
                target: 0,
            },
            {
                variable: 'target_list',
                source: 2,
                target: 1,
            },
            {
                variable: 'target_list',
                source: 3,
                target: 1,
            },
            {
                variable: 'dec',
                source: 4,
                target: 15,
            },
            {
                variable: 'dec',
                source: 4,
                target: 17,
            },
            {
                variable: 'target_list',
                source: 5,
                target: 4,
            },
            {
                variable: 'target_list',
                source: 6,
                target: 5,
            },
            {
                variable: 'target_list',
                source: 7,
                target: 5,
            },
            {
                variable: 'T',
                source: 8,
                target: 12,
            },
            {
                variable: 'time_zone',
                source: 9,
                target: 8,
            },
            {
                variable: 'd',
                source: 10,
                target: 12,
            },
            {
                variable: 'region',
                source: 11,
                target: 10,
            },
            {
                variable: 'LST',
                source: 12,
                target: 14,
            },
            {
                variable: 'long',
                source: 13,
                target: 12,
            },
            {
                variable: 'ha',
                source: 14,
                target: 15,
            },
            {
                variable: 'ha',
                source: 14,
                target: 17,
            },
            {
                variable: 'alt',
                source: 15,
                target: 17,
            },
            {
                variable: 'lat',
                source: 16,
                target: 15,
            },
            {
                variable: 'lat',
                source: 18,
                target: 17,
            },
        ],
    },
}

// Dispatch 699d2cb1-0776-4c54-a958-0a79082497e4
graphDemoData["699d2cb1-0776-4c54-a958-0a79082497e4"] = {
    "dispatch_id": "699d2cb1-0776-4c54-a958-0a79082497e4",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "identity",
                "node_id": 0,
                "started_at": "2022-10-03 03:34:56.953333",
                "completed_at": "2022-10-03 03:34:56.988396",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1",
                "node_id": 1,
                "started_at": "2022-10-03 03:34:56.937558",
                "completed_at": "2022-10-03 03:34:56.937562",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": ":sublattice:SubEta",
                "node_id": 2,
                "started_at": "2022-10-03 03:34:57.017045",
                "completed_at": "2022-10-03 03:34:57.430926",
                "status": "COMPLETED",
                "type": "sublattice",
                "executor_label": "local",
                "sublattice_dispatch_id": "e8096480-15da-41c3-b869-212e7e773749"
            },
            {
                "id": 3,
                "name": ":sublattice:SubBeta",
                "node_id": 3,
                "started_at": "2022-10-03 03:34:57.444964",
                "completed_at": "2022-10-03 03:34:58.142049",
                "status": "COMPLETED",
                "type": "sublattice",
                "executor_label": "local",
                "sublattice_dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0"
            }
        ],
        "links": [
            {
                "edge_name": "arg[0]",
                "parameter_type": "arg",
                "target": 2,
                "source": 0,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 0,
                "source": 1,
                "arg_index": 0
            },
            {
                "edge_name": "arg[0]",
                "parameter_type": "arg",
                "target": 3,
                "source": 2,
                "arg_index": 0
            }
        ]
    }
}


// Dispatch e8096480-15da-41c3-b869-212e7e773749
graphDemoData["e8096480-15da-41c3-b869-212e7e773749"] = {
    "dispatch_id": "e8096480-15da-41c3-b869-212e7e773749",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "identity",
                "node_id": 0,
                "started_at": "2022-10-03 03:34:57.202052",
                "completed_at": "2022-10-03 03:34:57.261796",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": ":parameter:1",
                "node_id": 1,
                "started_at": "2022-10-03 03:34:57.152237",
                "completed_at": "2022-10-03 03:34:57.152243",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": "identity",
                "node_id": 2,
                "started_at": "2022-10-03 03:34:57.214856",
                "completed_at": "2022-10-03 03:34:57.275284",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": ":parameter:1",
                "node_id": 3,
                "started_at": "2022-10-03 03:34:57.173495",
                "completed_at": "2022-10-03 03:34:57.173497",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": "identity",
                "node_id": 4,
                "started_at": "2022-10-03 03:34:57.242464",
                "completed_at": "2022-10-03 03:34:57.386979",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": ":parameter:1",
                "node_id": 5,
                "started_at": "2022-10-03 03:34:57.188510",
                "completed_at": "2022-10-03 03:34:57.188513",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 0,
                "source": 1,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 2,
                "source": 3,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 4,
                "source": 5,
                "arg_index": 0
            }
        ]
    }
}

// Dispatch 419d22a3-e1d7-46a8-92ba-d4ef234674b0
graphDemoData["419d22a3-e1d7-46a8-92ba-d4ef234674b0"] = {
    "dispatch_id": "419d22a3-e1d7-46a8-92ba-d4ef234674b0",
    "graph": {
        "nodes": [
            {
                "id": 0,
                "name": "identity",
                "node_id": 0,
                "started_at": "2022-10-03 03:34:57.960289",
                "completed_at": "2022-10-03 03:34:58.006827",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 1,
                "name": "electron list",
                "node_id": 1,
                "started_at": "2022-10-03 03:34:57.840132",
                "completed_at": "2022-10-03 03:34:57.907292",
                "status": "COMPLETED",
                "type": "electron_list",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 2,
                "name": ":parameter:1",
                "node_id": 2,
                "started_at": "2022-10-03 03:34:57.678650",
                "completed_at": "2022-10-03 03:34:57.678654",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 3,
                "name": ":parameter:1",
                "node_id": 3,
                "started_at": "2022-10-03 03:34:57.697728",
                "completed_at": "2022-10-03 03:34:57.697731",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 4,
                "name": ":parameter:1",
                "node_id": 4,
                "started_at": "2022-10-03 03:34:57.717116",
                "completed_at": "2022-10-03 03:34:57.717118",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 5,
                "name": "identity",
                "node_id": 5,
                "started_at": "2022-10-03 03:34:57.984383",
                "completed_at": "2022-10-03 03:34:58.046638",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 6,
                "name": "electron list",
                "node_id": 6,
                "started_at": "2022-10-03 03:34:57.854587",
                "completed_at": "2022-10-03 03:34:57.925453",
                "status": "COMPLETED",
                "type": "electron_list",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 7,
                "name": ":parameter:1",
                "node_id": 7,
                "started_at": "2022-10-03 03:34:57.735275",
                "completed_at": "2022-10-03 03:34:57.735277",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 8,
                "name": ":parameter:1",
                "node_id": 8,
                "started_at": "2022-10-03 03:34:57.755331",
                "completed_at": "2022-10-03 03:34:57.755334",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 9,
                "name": ":parameter:1",
                "node_id": 9,
                "started_at": "2022-10-03 03:34:57.771624",
                "completed_at": "2022-10-03 03:34:57.771626",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 10,
                "name": "identity",
                "node_id": 10,
                "started_at": "2022-10-03 03:34:58.021597",
                "completed_at": "2022-10-03 03:34:58.084013",
                "status": "COMPLETED",
                "type": "function",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 11,
                "name": "electron list",
                "node_id": 11,
                "started_at": "2022-10-03 03:34:57.882949",
                "completed_at": "2022-10-03 03:34:57.970101",
                "status": "COMPLETED",
                "type": "electron_list",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 12,
                "name": ":parameter:1",
                "node_id": 12,
                "started_at": "2022-10-03 03:34:57.788478",
                "completed_at": "2022-10-03 03:34:57.788481",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 13,
                "name": ":parameter:1",
                "node_id": 13,
                "started_at": "2022-10-03 03:34:57.804733",
                "completed_at": "2022-10-03 03:34:57.804735",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            },
            {
                "id": 14,
                "name": ":parameter:1",
                "node_id": 14,
                "started_at": "2022-10-03 03:34:57.821583",
                "completed_at": "2022-10-03 03:34:57.821585",
                "status": "COMPLETED",
                "type": "parameter",
                "executor_label": "local",
                "sublattice_dispatch_id": null
            }
        ],
        "links": [
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 0,
                "source": 1,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 1,
                "source": 2,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 1,
                "source": 3,
                "arg_index": 1
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 1,
                "source": 4,
                "arg_index": 2
            },
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 5,
                "source": 6,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 7,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 8,
                "arg_index": 1
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 6,
                "source": 9,
                "arg_index": 2
            },
            {
                "edge_name": "x",
                "parameter_type": "arg",
                "target": 10,
                "source": 11,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 12,
                "arg_index": 0
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 13,
                "arg_index": 1
            },
            {
                "edge_name": "x",
                "parameter_type": "kwarg",
                "target": 11,
                "source": 14,
                "arg_index": 2
            }
        ]
    }
}

export default graphDemoData
