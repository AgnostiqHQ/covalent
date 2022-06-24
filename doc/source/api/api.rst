.. currentmodule:: covalent
############
Covalent API
############

The following API documentation describes how to use Covalent.

- :ref:`electrons_api` and :ref:`lattices_api` are used for constructing workflows
- :ref:`local_executor` is used to execute electrons locally
- :ref:`deps_bash` are used to specify optional pre-execution shell commands for an electron
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

.. _deps_bash:

Bash Dependencies
""""""""""""""""""

Shell commands to run before an electron

.. autoclass:: covalent._workflow.depsbash.DepsBash
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
