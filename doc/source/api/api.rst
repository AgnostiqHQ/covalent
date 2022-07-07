.. currentmodule:: covalent
############
Covalent API
############

The following API documentation describes how to use Covalent.

- :ref:`electrons_api` and :ref:`lattices_api` are used for constructing workflows
- :ref:`local_executor` is used to execute electrons locally
- :ref:`file_transfer` is used to queue remote or local file transfer operations prior or post electron execution.
- :ref:`file_transfer_strategies` are used to perform download/upload/copy operations over various protocols.
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

.. _file_transfer:

File Transfer
"""""""""""""""""""""""""""

File Transfer from (source) and to (destination) local or remote files prior/post electron execution. Instances are are provided to `files` keyword argument in an electron decorator.

.. autoclass:: covalent._file_transfer.file.File
    :members:
    :inherited-members:

.. autoclass:: covalent._file_transfer.folder.Folder
    :members:
    :inherited-members:

.. autoclass:: covalent._file_transfer.file_transfer.FileTransfer
    :members:
    :inherited-members:

.. autofunction:: covalent._file_transfer.file_transfer.TransferFromRemote

.. autofunction:: covalent._file_transfer.file_transfer.TransferToRemote

----------------------------------------------------------------

.. _file_transfer_strategies:

File Transfer Strategies
"""""""""""""""""""""""""""

A set of classes with a shared interface to perform copy, download, and upload operations given two (source & destination) File objects that support various protocols.


.. autoclass:: covalent._file_transfer.strategies.transfer_strategy_base.FileTransferStrategy
    :members:
    :inherited-members:

.. autoclass:: covalent._file_transfer.strategies.rsync_strategy.Rsync
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
