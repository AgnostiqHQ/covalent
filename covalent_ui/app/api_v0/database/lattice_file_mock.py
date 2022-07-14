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

import os

user = os.getlogin()


def file_read():
    file_reads = {
        "result": [[[1009680240, -1347578900.271903], -1034576156.5074124], -1940182273],
        "inputs": "target_list=['sirius', 'trappist-1']",
        "error": """Node task(0) failed: Traceback (most recent call last): File "/home/aravindprabaharan/Desktop/workbench/covalent/covalent/covalent_dispatcher/_core/execution.py", line 222, in _run_task output, stdout, stderr = executor.execute( File "/home/aravindprabaharan/Desktop/workbench/covalent/covalent/covalent/executor/executor_plugins/dask.py", line 136, in execute result = future.result() File "/home/aravindprabaharan/.local/lib/python3.8/site-packages/distributed/client.py", line 238, in result raise exc.with_traceback(tb) File "fail_dispatch.py", line 6, in task ZeroDivisionError: division by zero """,
        "function_string": [
            """"@ct.lattice arr = array.array('i', [1, 2, 3]) # printing original array print ("The new created array is : ",end="") for i in range (0,3): print (arr[i], end=" ") print ("\r")""",
            """@ct.lattice import numpy as cova b = cova.zeros(2, dtype = int) print("Matrix b : \n", b) a = cova.zeros([2, 2], dtype = int) print("\nMatrix a : \n", a) c = cova.zeros([3, 3]) print("\nMatrix c : \n", c)""",
            """@ct.lattice import numpy # initializing matrices x = numpy.array([[1, 2], [4, 5]]) y = numpy.array([[7, 8], [9, 10]]) # using add() to add matrices print ("The element wise addition of matrix is : ") print (numpy.add(x,y)) # using subtract() to subtract matrices print ("The element wise subtraction of matrix is : ") print (numpy.subtract(x,y)) # using divide() to divide matrices print ("The element wise division of matrix is : ") print (numpy.divide(x,y)) print("\nMatrix a : \n", a) c = cova.zeros([3, 3]) print("\nMatrix c : \n", c)""",
            """@ct.lattice from tkinter import * from tkinter.ttk import * from time import strftime # creating tkinter window root = Tk() # Adding widgets to the root window Label(root, text = 'covasforcovas', font =('Verdana', 15)).pack(side = TOP, pady = 10) Button(root, text = 'Click Me !').pack(side = TOP) mainloop() # using add() to add matrices print ("The element wise addition of matrix is : ") print (numpy.add(x,y)) # using subtract() to subtract matrices print ("The element wise subtraction of matrix is : ") print (numpy.subtract(x,y)) # using divide() to divide matrices print ("The element wise division of matrix is : ") print (numpy.divide(x,y)) print("\nMatrix a : \n", a) c = cova.zeros([3, 3]) print("\nMatrix c : \n", c)""",
        ],
        "executor_details": {
            "log_stdout": "stdout.log",
            "log_stderr": "stderr.log",
            "conda_env": "",
            "cache_dir": f"/home/{user}/.cache/covalent",
            "current_env_on_conda_fail": False,
            "current_env": "",
            "scheduler_address": "tcp://127.0.0.1:44851",
        },
    }
    return file_reads
