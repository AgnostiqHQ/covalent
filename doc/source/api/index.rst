.. currentmodule:: covalent
############
Covalent API
############

.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Basics:

   covalent
   cli
   electrons
   lattice
   dispatcher
   results
   leptons
   executors/index
   deps
   data_transfers
   triggers
   config
   cancel

The following API documentation describes how to use Covalent.

- :ref:`electrons_api` and :ref:`lattices_api` are used for constructing workflows
- :ref:`local_executor` is used to execute electrons locally
- :ref:`file_transfer` is used to queue remote or local file transfer operations prior or post electron execution.
- :ref:`file_transfer_strategies` are used to perform download/upload/copy operations over various protocols.
- :ref:`dask_executor` is used to execute electrons in a Dask cluster
- :ref:`triggers` are used to execute a workflow triggered by a specific type of event
- :ref:`deps` are used to specify any kind of electron dependency
- :ref:`deps_pip` are used to specify PyPI packages that are required to run an electron
- :ref:`deps_bash` are used to specify optional pre-execution shell commands for an electron
- :ref:`deps_call` are used to specify functions or dependencies that are called in an electron's execution environment
- :ref:`results_interface` is used for collecting and manipulating results
- :ref:`dispatcher_interface` is used for dispatching workflows
- The :ref:`dispatcher_server_api` is used for interfacing with the Covalent server
- The :ref:`cancellation` API is used for canceling dispatches and individual tasks within a workflow
