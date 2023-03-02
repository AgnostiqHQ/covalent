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

1. A task is failing to execute due to a runtime error arising from the task definition.

    - Check the logs of the Covalent server to see if there are any errors.


2. The executor memory and compute resources are insufficient. For a memory issues with the Dask executor, the allocated memory per worker needs to increased via (provided the user has enough memory available):

    .. code-block::

        covalent start -n 4 -m "2GB" -d

Check out this `discussion <https://github.com/AgnostiqHQ/covalent/discussions/1246>`_ for more details.


3. Some larger workflows fail for MacOS users due to a `too many open files in system` error. This can be resolved by increasing the open file limit via the terminal command ``ulimit -n 10240`` and restarting Covalent.


-----------------------------
Covalent server not starting
-----------------------------

The Covalent server can fail to start when running ``covalent start`` when Covalent is being attempted to be run outside a virtual environment. In this case, even after covalent was started with ``covalent start``, ``covalent status`` will report that the server is not running.

This can be fixed by running ``covalent start`` inside a pyenv/conda virtual environment .


------------------------------------------
Covalent CLI commands throws error/warning
------------------------------------------

1. The covalent config file can periodically get corrupted due to multiple processes attempting to modify the config file simultaneously. This can sometimes be fixed by manually editing the config file. However, if this does not work, the user can delete the config file and restart the Covalent server.

.. warning::

    The user also has the option of running ``covalent purge`` which will delete the config file. A new config file will be created when the user runs ``covalent start`` again. This option must be used with caution.

2. If DB migration error is thrown, that implies that the database schema is not up to date with the latest version of Covalent. This can be fixed by running ``covalent db migrate``.


-----------------------------------------
Get result throws error when wait is True
-----------------------------------------

# TODO: Get more info


----------------------------------
Executor issues after installation
----------------------------------

1. Users can get ``executor not found`` or ``Covalent config file missing default values`` for the executor if Covalent was not restarted after the executor was installed. This can be fixed by restarting the Covalent server.


------------------------------------------
Long running workflow with max-depth issue
------------------------------------------

# TODO: Get more info
