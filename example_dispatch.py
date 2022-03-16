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

"""
An example script containing a simple workflow that can be dispatched to Covalent
"""

import time
import covalent as ct
import covalent_dispatcher._cli.service as service
from requests import request


@ct.electron
def join_words(a, b):
    return ", ".join([a, b])


@ct.electron
def excitement(a):
    return f"{a}!"


@ct.lattice
def simple_workflow(a, b):
    phrase = join_words(a, b)
    return excitement(phrase)

if service._is_server_running():
    print('Dispatcher service has started')
else:
    print('Dispatcher service is starting...')
    time.sleep(15)

dispatch_id = ct.dispatch(simple_workflow, dispatcher_addr='localhost:48008')("Hello", "Covalent")
results_url = "http://localhost:48008/api/results"
results = request("GET", results_url, headers={}, data={}).json()
dispatch_result = results[0]['result'] if results else None
dispatch_status = results[0]['status'] if results else None
print(f'Dispatch {dispatch_id} was executed successfully with status: {dispatch_status}')
print(f'The result of the dispatch is: {dispatch_result}')
