############
How-to Guide
############

This guide is a collection of step-by-step instructions for tasks that are commonly (and in some cases not so commonly) encountered when using Covalent.

It covers specific tasks at every phase of the workflow development process:

1. Constructing workflows
2. Executing workflows, including using and writing executors
3. Querying Status and Collecting and Viewing Results
4. Saving and Working with Result Files

At the end are how-tos on miscellaneous topics including configuration and troubleshooting.

Constructing Workflows
**********************

:doc:`Constructing a Task (Electron) <./coding/construct_electron>`

:doc:`Constructing a Workflow (Lattice) <./coding/construct_lattice>`

:doc:`Adding an Electron to a Lattice <./coding/add_electron_to_lattice>`

:doc:`Testing an Electron <./coding/test_electron>`

:doc:`Using an Iterable <./coding/use_iterable>`

:doc:`Looping <./coding/looping>`

:doc:`Visualizing a Lattice <./coding/visualize_lattice>`

:doc:`Adding Constraints to Tasks and Workflows <./coding/add_constraints_to_lattice>`

:doc:`Waiting For Execution of Another Electron <./coding/wait_for_another_electron>`

:doc:`Transferring Local Files During Workflows<./coding/file_transfers_for_workflows_local>`

:doc:`Transferring Remote Files During Workflows<./coding/file_transfers_to_remote>`

:doc:`Transferring Files to and from an S3 Bucket<./coding/file_transfers_to_from_s3>`

:doc:`Constructing a Lepton <./coding/construct_lepton>`

:doc:`Using C Code (Leptons)<./coding/construct_c_task>`

:doc:`Adding Pip Dependencies to an Electron <./coding/add_pip_dependencies_to_electron>`

:doc:`Adding Bash Dependencies to an Electron <./coding/add_bash_dependencies_to_electron>`

:doc:`Adding Callable Function Dependencies to an Electron <./coding/add_callable_dependencies_to_electron>`

:doc:`Constructing Task from Bash Scripts <./coding/construct_bash_task>` x

Executing a Workflow
********************

:doc:`Managing the Covalent Server <./execution/covalent_cli>`

:doc:`Running a Workflow (Lattice) <./execution/execute_lattice>`

:doc:`Executing an Individual Electron <./execution/execute_individual_electron>`

:doc:`Executing a Lattice Multiple Times <./execution/execute_lattice_multiple_times>`

:doc:`Executing Multiple Lattices <./execution/execute_multiple_lattices>` x

:doc:`Executing a Lattice as an Electron (Sublattice) <./execution/execute_sublattice>`

:doc:`Choosing an Executor For a Task <./execution/choosing_executors>`

:doc:`Creating a Custom Executor <./execution/creating_custom_executors>` x

:doc:`Canceling a Running Workflow <./execution/cancel_dispatch>` x

:doc:`Executing an Electron in a Conda Environment <./execution/choosing_conda_environments>` x

Querying and Viewing
********************

:doc:`Querying the Status of a Lattice in a Notebook<./status/query_lattice_execution_status>`

:doc:`Querying the Status of an Electron in a Notebook<./status/query_electron_execution_status>`

:doc:`Querying Lattice Execution Time <./status/query_lattice_execution_time>`

:doc:`Querying Multiple Workflows (Lattices)<./collection/query_multiple_lattice_execution_results>`

:doc:`Getting Results of Previous Workflow Dispatches <./collection/query_lattice_execution_result>`

:doc:`Getting the Result of a Task (Electron) <./collection/query_electron_execution_result>`

Configuration
*************

:doc:`Customizing the Configuration <./config/customization>` x

Database
********

:doc:`What To Do When Encountering Database Migration Errors <./db/migration_error>` x

----------------------------------

Is anything missing? Contribute a guide on `GitHub <https://github.com/AgnostiqHQ/covalent/issues>`_.
