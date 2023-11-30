.. currentmodule:: covalent

############
Covalent API
############

The following API documentation describes how to use Covalent.

- The :ref:`covalent_server` manages workflow dispatch, orchestration, and metadata
- :ref:`electrons_api` and :ref:`lattices_api` are used for constructing workflows
- :ref:`qelectrons_api` are used to customize and track quantum circuit execution
- :ref:`qclusters_api` are used to distribute Quantum Electrons across multiple quantum backends.
- :ref:`local_executor` is used to execute electrons locally
- :ref:`file_transfer` is used to queue remote or local file transfer operations prior or post electron execution.
- :ref:`file_transfer_strategies` are used to perform download/upload/copy operations over various protocols.
- :ref:`triggers` are used to execute a workflow triggered by a specific type of event
- :ref:`dask_executor` is used to execute electrons in a Dask cluster
- :ref:`deps` are used to specify any kind of electron dependency
- :ref:`deps_pip` are used to specify PyPI packages that are required to run an electron
- :ref:`deps_bash` are used to specify optional pre-execution shell commands for an electron
- :ref:`deps_call` are used to specify functions or dependencies that are called in an electron's execution environment
- :ref:`results_interface` is used for collecting and manipulating results
- :ref:`dispatcher_interface` is used for dispatching workflows and stopping triggered dispatches
- The :ref:`dispatcher_server_api` is used for interfacing with the Covalent server

.. _covalent_server:

Covalent Server
"""""""""""""""""""""""""""
A Covalent server must be running in order to dispatch workflows. The Covalent CLI provides various utilities for starting, stopping, and managing a Covalent server. For more information, see:

.. code-block:: bash

    covalent --help

The Covalent SDK also includes a Python interface for starting and stopping the Covalent server.

.. autofunction:: covalent._programmatic.commands.is_covalent_running


.. autofunction:: covalent._programmatic.commands.covalent_start


.. autofunction:: covalent._programmatic.commands.covalent_stop


----------------------------------------------------------------

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

.. _qelectrons_api:

Quantum Electrons
"""""""""""""""""""""""""""

.. autodecorator:: covalent.qelectron


----------------------------------------------------------------

.. _qclusters_api:

Quantum Clusters
"""""""""""""""""""""""""""

.. autopydantic_model:: covalent.executor.QCluster


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

File Transfer from (source) and to (destination) local or remote files prior/post electron execution. Instances are provided to `files` keyword argument in an electron decorator.

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

.. _triggers:

Triggers
"""""""""

Execute a workflow triggered by a specific type of event

.. automodule:: covalent.triggers
   :imported-members:
   :members:
   :undoc-members:
   :show-inheritance:

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

Index
#####

:doc:`Here<./index>` is an alphabetical index.

Contents
########

.. include:: ./toc.rst


API
###

.. _workflow_components_api:
.. include:: ./section_workflow_components.rst


.. _task_helpers_api:
.. include:: ./section_task_helpers.rst


.. _executors_api:
.. include:: ./section_executors.rst


.. _dispatch_infrastructure_api:
.. include:: ./section_dispatch_infrastructure.rst


.. _covalent_cli_tool_api:
.. include:: ./section_covalent_cli_tool.rst


.. toctree::
   :maxdepth: 1
   :hidden:

   section_workflow_components
   section_task_helpers
   section_executors
   section_dispatch_infrastructure
   section_covalent_cli_tool
