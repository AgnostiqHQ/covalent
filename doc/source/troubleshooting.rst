#####################
Troubleshooting guide
#####################

This page is dedicated to solutions to common issues encountered when using the Covalent platform.


1. Workflow hanging

2. Workflow failing

3. Covalent server not starting

4. Covalent CLI commands throws error

    - Due to config corruption.

5. DB migration warning

6. Get result throws error when wait is True

7. Executor issues after installation

 - Restart Covalent server







----------------------
Dispatcher server logs
----------------------

Users can get more information on the status of their Covalent workflow by starting the Dispatcher server with `covalent start -d` and then running the following command in the terminal with `covalent logs`.

Note that in the future, these logs will be available in the Covalent UI.


--------------------------------------------
Increase open file limit for large workflows
--------------------------------------------

MacOS users can experience errors of the form `Too many open files in system`. In order to resolve this issue simply change the open file limit via the terminal command `ulimit -n 10240` and restart Covalent.


--------------------------
Dask cluster worker memory
--------------------------

Some tasks can fail to execute due to insufficient memory allocated to each worker. This can be resolved by increasing the memory allocated to each worker via:

.. code-block::

    covalent start -n 4 -m "2GB" -d

Check out this [discussion](https://github.com/AgnostiqHQ/covalent/discussions/1246) for more info.


--------------------------------
More information on Dask cluster
--------------------------------

To get more information on Dask clusters, users can install `bokeh` via

.. code-block::

    pip install bokeh




------------------------------------------
Long running workflow with max-depth issue
------------------------------------------

# TODO: Get more info


----------------------------------------
Using Covalent with virtual environments
----------------------------------------

Covalent start has been called but status reports that it hasn't started.
