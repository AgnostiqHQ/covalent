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
# Relief from the License may be granted by purchasing a commercial license.
"""Lattice Result Sample Data"""


def lattice_result():
    """Lattice Results Sample List"""
    lattice_results_list = {
        "files": [
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac16",
                "result": [[[1009680240, -1347578900.271903], -1034576156.5074124], -1940182273],
                "output": None,
                "input": "target_list=['sirius', 'trappist-1']",
                "failed": None,
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac17",
                "result": [-1585698906.914249],
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac18",
                "result": [
                    -1203580315,
                    1987774889,
                    [-242000060, [570788314, -1105065004, 28166334.282756805], 1153975479.8294501],
                ],
                "output": None,
                "input": "LST=<covalent._workflow.electron.Electron object at 0x7f5e8258f1c0>, RA=<covalent._workflow.electron.Electron object at 0x7f5e61fa19a0>",
                "failed": None,
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac19",
                "result": [-2076729431, -568849912],
                "output": {
                    "head": "get_azimuth [stderr]",
                    "message": "star_tracker_example.py:124: RuntimeWarning: invalid value encountered in arccos",
                },
                "input": None,
                "failed": """Node task(0) failed: Traceback (most recent call last): File "/home/aravindprabaharan/Desktop/workbench/covalent/covalent/covalent_dispatcher/_core/execution.py", line 222, in _run_task output, stdout, stderr = executor.execute( File "/home/aravindprabaharan/Desktop/workbench/covalent/covalent/covalent/executor/executor_plugins/dask.py", line 136, in execute result = future.result() File "/home/aravindprabaharan/.local/lib/python3.8/site-packages/distributed/client.py", line 238, in result raise exc.with_traceback(tb) File "fail_dispatch.py", line 6, in task ZeroDivisionError: division by zero """,
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac20",
                "result": [[[1009680240, -1347578900.271903], -1034576156.5074124], -1940182273],
                "output": None,
                "input": "n=5, parallel=True, serial=True",
                "failed": None,
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac21",
                "result": [[376718713, 389085837], 914308183],
                "output": None,
                "input": "n=5, parallel=True, serial=True",
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac22",
                "result": [{"blanket": -308570231, "led": -1076083660.121066}, -133715356],
                "output": {
                    "head": "get_azimuth [stderr]",
                    "message": "star_tracker_example.py:124: RuntimeWarning: invalid value encountered in arccos",
                },
                "input": "n=5, parallel=True, serial=True",
                "failed": "get_RA: substring not found",
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac23",
                "result": {
                    "partly": {"combination": 620213845, "mouse": 1670773079.9317193},
                    "sleep": {"amount": 1447576728.8193715, "manner": 638591855},
                },
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac24",
                "result": [[[1009680240, -1347578900.271903], -1034576156.5074124], -1940182273],
                "output": None,
                "input": "districtapi=https://api.covid19india.org/state_district_wise.json, stateapi=https://api.covid19india.org/data.json",
                "failed": None,
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac25",
                "result": [[[1009680240, -1347578900.271903], -1034576156.5074124], -1940182273],
                "output": {
                    "head": "get_azimuth [stderr]",
                    "message": "star_tracker_example.py:124: RuntimeWarning: invalid value encountered in arccos",
                },
                "input": None,
                "failed": "substring not found",
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac26",
                "result": {
                    "give": {
                        "load": {"declared": -1355831037.400295, "cent": -2068602736},
                        "mathematics": 241719047,
                    },
                    "tropical": 51076894,
                },
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac27",
                "result": {"handle": 175407690, "square": -160934466},
            },
            {
                "dispatch_id": "1b44989a-1c65-4148-959e-00062a34ac28",
                "result": [[[1309680240, -1247578900.271903], -1034576156.50], -190182273],
                "output": None,
                "input": "n=2, parallel=True, serial=True",
                "failed": None,
            },
        ]
    }
    return lattice_results_list
