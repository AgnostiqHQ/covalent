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

const demoDashboardListData = {
    dashboardOverview: {
        "total_jobs": 6,
        "total_jobs_running": 0,
        "total_jobs_completed": 5,
        "total_jobs_failed": 1,
        "latest_running_task_status": "COMPLETED",
        "total_dispatcher_duration": 53000
    },
    dashboardList: [
        {
            "dispatch_id": "2537c3b0-c150-441b-81c6-844e3fd88ef3",
            "lattice_name": "final_calc",
            "runtime": 1000,
            "total_electrons": 10,
            "total_electrons_completed": 10,
            "started_at": "2022-08-11T12:14:39",
            "ended_at": "2022-08-11T12:14:40",
            "status": "COMPLETED",
            "updated_at": "2022-08-11T12:14:40"
        },
        {
            "dispatch_id": "ba3c238c-cb92-48e8-b7b2-debeebe2e81a",
            "lattice_name": "final_calc",
            "runtime": 1000,
            "total_electrons": 10,
            'total_electrons_completed': 6,
            "started_at": "2022-08-10T12:14:39",
            "ended_at": "2022-08-10T12:14:40",
            'status': "FAILED",
            'updated_at': "2022-08-11T12:14:40"
        },
        {
            "dispatch_id": "fcd385e2-7881-4bcd-862c-2ac99706d2f9",
            "lattice_name": "compute_energy",
            "runtime": 13000,
            "total_electrons": 8,
            "total_electrons_completed": 8,
            "started_at": "2022-06-15T10:14:40",
            "ended_at": "2022-06-15T10:14:53",
            "status": "COMPLETED",
            "updated_at": "2022-08-11T12:14:40"
        },
        {
            "dispatch_id": "b199afa5-301f-47d8-a8dc-fd78e1f5d08a",
            "lattice_name": "compute_energy",
            "runtime": 13000,
            "total_electrons": 8,
            "total_electrons_completed": 8,
            "started_at": "2022-06-11T08:14:10",
            "ended_at": "2022-06-11T08:14:23",
            "status": "COMPLETED",
            "updated_at": "2022-08-11T12:14:40"
        },
        {
            "dispatch_id": "eb2549cc-e2d4-482b-ba9e-c1cb39d0eb1a",
            "lattice_name": "compute_energy",
            "runtime": 13000,
            "total_electrons": 8,
            "total_electrons_completed": 8,
            "started_at": "2022-08-11T12:14:30",
            "ended_at": "2022-08-11T12:14:43",
            "status": "COMPLETED",
            "updated_at": "2022-08-11T12:14:40"
        },
        {
            "dispatch_id": "df4601e7-7658-4a14-a860-f91a35a1b453",
            "lattice_name": "compute_energy",
            "runtime": 13000,
            "total_electrons": 8,
            "total_electrons_completed": 8,
            "started_at": "2022-06-13T12:14:30",
            "ended_at": "2022-06-13T12:14:43",
            "status": "COMPLETED",
            "updated_at": "2022-08-11T12:14:40"
        }
    ],
    total_count: 6
}

export default demoDashboardListData
