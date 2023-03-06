#####################
Troubleshooting guide
#####################

This page is dedicated to solutions to common issues encountered when using the Covalent platform.


----------------
Workflow hanging
----------------

If a workflow is hanging, it is likely due to a task that is not completing. To get more information on the status of the workflow, users can check the details of the Covalent server via:

.. code-block:: bash

    covalent logs

.. note::

    In order to get more informative logs, users can start the Covalent server with ``covalent start -d``.

This may happen for a Local Executor since a worker process in ``ProcessPoolExecutor`` can stall sporadically without failing. In this case, the user needs to restart the server and resubmit the workflow.


-----------------
Workflow failing
-----------------

A workflow can fail for a number of reasons. The most common reasons are:

1. A task is failing to execute due to a runtime error arising from the task definition. In this case, check the logs of the Covalent server to see if there are any errors and the task error cards in the Covalent UI.


2. The executor memory and compute resources are insufficient. For a memory issues with the Dask executor, the allocated memory per worker needs to increased via (provided the user has enough memory available):

.. code-block::

    covalent start -n 4 -m "2GB" -d

Check out this `discussion <https://github.com/AgnostiqHQ/covalent/discussions/1246>`_ for more details.


3. Some larger workflows fail for MacOS users due to a `too many open files in system` error. This can be resolved by increasing the open file limit via the terminal command ``ulimit -n 10240`` and restarting Covalent.


-----------------------------
Covalent server not starting
-----------------------------

If dispatches are failing due to connection refused errors after running ``covalent start`` it is possible the covalent server was unable to start.

1. Ensure that you are able to run the ``python`` command and that ``python --version`` is compatible with covalent refer to `compatibility <https://covalent.readthedocs.io/en/latest/getting_started/compatibility.html>`_ section. If your python version is not compatible or if you only have ``python3`` installed it is recommended that a virtual environment is used (several tools can also be leveraged for this: poetry, conda, pyenv, ect.)

Users should ultimately check ``covalent logs`` for more information and submit a new issue on Github `discussion <https://github.com/AgnostiqHQ/covalent/issues>`_ with any relevant log information associated with the issue.

------------------------------------------
Covalent CLI commands throws error/warning
------------------------------------------

1. The covalent config file can periodically get corrupted due to multiple processes attempting to modify the config file simultaneously. This can sometimes be fixed by manually editing the config file. However, if this does not work, the user can delete the config file and restart the Covalent server.

.. warning::

    The user also has the option of running ``covalent purge`` which will delete the config file. A new config file will be created when the user runs ``covalent start`` again. This option must be used with caution.

2. If DB migration error is thrown, that implies that the database schema is not up to date with the latest version of Covalent. This can be fixed by running ``covalent db migrate``. For more information, check out :doc:`What To Do When Encountering Database Migration Errors <./how_to/db/migration_error>`.


-----------------------------------------
Getting Result fails for long workflows
-----------------------------------------

1. For long-running workflows if a user runs ``get_result`` synchronously with ``wait=True`` and observes a ``RecursionError: maximum recursion depth exceeded`` error this means that the result may still be pending or complete but covalent failed during the polling process. Users should still be able to re-run the command to continue waiting for a workflow result.



----------------------------------
Executor issues after installation
----------------------------------

1. Users can get ``executor not found`` or ``Covalent config file missing default values`` for the executor if Covalent was not restarted after the executor was installed. This can be fixed by restarting the Covalent server.


-------------------------------------------------------
Lattice not found error when using Self-hosted Covalent
-------------------------------------------------------

1. Errors related to the lattice not being found arise from the user trying to retrieve / access data corresponding to a dispatch id that does not exist in the database. This can happen when the self-hosted and local Covalent servers get mixed up. This can be avoided by explicitly specifying the dispatcher address when dispatching and retrieving results.

.. note::

    In general, users should set the ``dispatcher_addr`` in the ``ct.dispatch()/ct.get_result()`` functions rather than using ct.set_config if they'd like to only temporarily change the dispatcher address.


2. The dispatch id is invalid.


--------------------------------------------------------
Connection timeout error when using Self-hosted Covalent
--------------------------------------------------------

If a user is getting a connection timeout error while using self-hosted Covalent, it is likely that the local and self-hosted servers are getting mixed up. In this case, the user needs to ensure that the dispatcher address is explicitly set and that the corresponding Covalent server is actually running.
