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
   qelectrons
   qclusters
   executors/index
   deps
   data_transfers
   triggers
   config
   cancel

The following API documentation describes how to use Covalent.

- :ref:`electrons_api` and :ref:`lattices_api` are used for constructing workflows
- :ref:`qelectrons_api` are used to customize and track quantum circuit execution
- :ref:`qclusters_api` are used to distribute Quantum Electrons across multiple quantum backends.
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
- The :ref:`cancel` API is used for canceling dispatches and individual tasks within a workflow


##################
Covalent API Index
##################

:ref:`AsyncBaseExecutor<base_exec_async_api>`

:ref:`AWSBatchExecutor<aws_batch_api>`

:ref:`AWSLambdaExecutor<awslambda_api>`

:ref:`AzureBatchExecutor<azurebatch_api>`

:ref:`BraketExecutor<awsbraket_api>`

:ref:`cancel<cancel_api>`

:ref:`Covalent CLI Tool<cli_tool_api>`

:ref:`DaskExecutor<dask_executor>`

:ref:`Deps<deps_api>`

:ref:`DepsBash<deps_bash_api>`

:ref:`DepsCall<deps_call_api>`

:ref:`DepsPip<deps_pip_api>`

:ref:`Dispatcher<dispatcher_interface_api>`

:ref:`EC2Executor<awsec2_executor>`

:ref:`ECSExecutor<awsecs_executor>`

:ref:`Electron <electrons_api>`

:ref:`FileTransfer<file_transfer_api>`

:ref:`FileTransferStrategy<file_transfer_strategy_api>`

:ref:`GCPBatchExecutor<gcpbatch_api>`

:ref:`Lattice <lattices_api>`

:ref:`Lepton <leptons_api>`

:ref:`LocalExecutor<local_executor_api>`

:ref:`Result<results_interface_api>`

:ref:`SSHExecutor<ssh_executor>`

:ref:`SlurmExecutor<slurm_executor>`

:ref:`Trigger<triggers_api>`


Covalent CLI Tool
-----------------

- :ref:`cli_tool_api`
- :ref:`config_api`
