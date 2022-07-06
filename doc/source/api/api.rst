.. currentmodule:: covalent
############
Covalent API
############

The following API documentation describes how to use Covalent.

- :ref:`electrons_api` and :ref:`lattices_api` are used for constructing workflows
- :ref:`local_executor` is used to execute electrons locally
- :ref:`dask_executor` is used to execute electrons in a Dask cluster
- :ref:`deps` is used to specify any kind of electron dependency
- :ref:`deps_pip` is used to specify PyPI packages that are required to run an electron
- :ref:`deps_bash` is used to specify optional pre-execution shell commands for an electron
- :ref:`deps_call` is used to specify functions or dependencies that are called in an electron's execution environment
- :ref:`results_interface` is used for collecting and manipulating results
- :ref:`dispatcher_interface` is used for dispatching workflows
- The :ref:`dispatcher_server_api` is used for interfacing with the Covalent server

.. _electrons_api:

Electron
"""""""""""""""""""""""""""
.. autodecorator:: electron


.. autoclass:: covalent._workflow.electron.Electron
    :members:


----------------------------------------------------------------

.. _lattices_api:

Lattice
"""""""""""""""""""""""""""

.. autodecorator:: lattice


.. autoclass:: covalent._workflow.lattice.Lattice
    :members:

----------------------------------------------------------------


.. _local_executor:

Local Executor
"""""""""""""""""""""""""""

Executing tasks (electrons) directly on the local machine

.. autoclass:: covalent.executor.executor_plugins.local.LocalExecutor
    :members:
    :inherited-members:

----------------------------------------------------------------

.. _dask_executor:

Dask Executor
"""""""""""""""""""""""""""

Executing tasks (electrons) in a Dask cluster

.. autoclass:: covalent.executor.executor_plugins.dask.DaskExecutor
    :members:
    :inherited-members:

----------------------------------------------------------------

.. _deps:

Dependencies
""""""""""""""

Generic dependencies for an electron

.. autoclass:: covalent._workflow.deps.Deps
   :members:

----------------------------------------------------------------

.. _deps_pip:

Pip Dependencies
""""""""""""""""""

PyPI packages to be installed before executing an electron

.. autoclass:: covalent._workflow.depspip.DepsPip
   :members:

----------------------------------------------------------------

.. _deps_bash:

Bash Dependencies
""""""""""""""""""

Shell commands to run before an electron

.. autoclass:: covalent._workflow.depsbash.DepsBash
   :members:

----------------------------------------------------------------

.. _deps_call:

Call Dependencies
""""""""""""""""""

Functions, shell commands, PyPI packages, and other types of dependencies to be called in an electron's execution environment

.. autoclass:: covalent._workflow.depscall.DepsCall
   :members:

----------------------------------------------------------------

.. _dispatcher_interface:

Dispatcher
""""""""""""""

Dispatching jobs to the server

.. autofunction:: dispatch
.. autofunction:: dispatch_sync


----------------------------------------------------------------

.. _results_interface:

Results
""""""""""""""

Collecting and managing results

.. autofunction:: get_result


.. autoclass:: covalent._results_manager.result.Result
    :members:


----------------------------------------------------------------

.. currentmodule:: covalent_dispatcher

.. _dispatcher_server_api:

Covalent CLI Tool
""""""""""""""""""

This Command Line Interface (CLI) tool is used to manage Covalent server.

.. click:: covalent_dispatcher._cli.cli:cli
    :prog: covalent
    :commands: start,stop,restart,status,purge,logs
    :nested: full
