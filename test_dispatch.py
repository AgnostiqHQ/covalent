import time

import covalent as ct
from requests import request
import covalent_dispatcher._cli.service as service


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
    time.sleep(20)


dispatch_id = ct.dispatch(simple_workflow, dispatcher_addr='localhost:48008')("Hello", "Covalent")
print('Dispatch id is:', dispatch_id)
results_url = "http://localhost:48008/api/results"
results = request("GET", results_url, headers={}, data={}).json()
dispatch_result = results[0]['result'] if results else None
dispatch_status = results[0]['status'] if results else None
dispatch_id = ct.dispatch(simple_workflow, dispatcher_addr='localhost:48008')("Hello", "Covalent")
print(f'Dispatch {dispatch_id} was executed successfully with status: {dispatch_status}')
print(f'The result of the dispatch is: {dispatch_result}')


