############
How-to Guide
############

This guide is a collection of step-by-step instructions for tasks that are commonly (and in some cases not so commonly) encountered when using Covalent.

.. note:: Most of the how-to instructions below are Jupyter notebook files (formerly IPython files; they have an `ipynb` file extension). You can open a file and run the example on your local machine. To run an example:

    1. `Install Jupyter <https://jupyter.org/install>`_.
    2. :doc:`Install Covalent<../getting_started/quick_start/index>`.
    3. :doc:`Start the Covalent server<./execution/covalent_cli>`.
    4. Download the IPython (`.ipynb`) file by replacing `html` with `ipynb` in the How-to document URL. For example, change "https://covalent.readthedocs.io/en/stable/how_to/orchestration/construct_electron.html" to "https://covalent.readthedocs.io/en/stable/how_to/orchestration/construct_electron.ipynb"\.
    5. `Open the IPython (.ipynb) file in a Jupyter notebook <https://docs.jupyter.org/en/latest/running.html#how-do-i-open-a-specific-notebook>`_.

The guide covers specific tasks at every phase of the workflow development process:

1. :ref:`Constructing workflows <howto_coding>`
2. :ref:`Executing workflows <howto_executing>`, including using and writing executors
3. :ref:`Querying Status <howto_querying>` and :ref:`Collecting and Viewing Results <howto_querying>`

At the end are how-tos on miscellaneous topics including :ref:`configuration <howto_config>`.

.. _howto_coding:

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

:doc:`Transferring Files To and From a Remote Host<./coding/file_transfers_to_from_remote>`

:doc:`Transferring Files To and From an S3 Bucket<./coding/file_transfers_to_from_s3>`

:doc:`Transferring Files To and From Azure Blob Storage<./coding/file_transfers_to_from_azure_blob>`

:doc:`Transferring Files To and From Google Cloud Storage<./coding/file_transfers_to_from_gcp_storage>`

:doc:`Constructing a Lepton <./coding/construct_lepton>`

:doc:`Using C Code (Leptons)<./coding/construct_c_task>`

:doc:`Adding Pip Dependencies to an Electron <./coding/add_pip_dependencies_to_electron>`

:doc:`Adding Bash Dependencies to an Electron <./coding/add_bash_dependencies_to_electron>`

:doc:`Adding Callable Function Dependencies to an Electron <./coding/add_callable_dependencies_to_electron>`

:doc:`Constructing a Task from Bash Scripts <./coding/construct_bash_task>`

:doc:`How to add a directory trigger to a lattice <./coding/dir_trigger>`

:doc:`How to add a time trigger to a lattice <./coding/time_trigger>`

.. _howto_executing:

Executing a Workflow
********************

:doc:`Managing the Covalent Server <./execution/covalent_cli>`

:doc:`Running a Workflow (Lattice) <./execution/execute_lattice>`

:doc:`Re-executing a Workflow <./execution/redispatch>`

:doc:`Executing an Individual Electron <./execution/execute_individual_electron>`

:doc:`Executing a Lattice Multiple Times <./execution/execute_lattice_multiple_times>`

:doc:`Executing Multiple Lattices <./execution/execute_multiple_lattices>`

:doc:`Executing a Lattice as an Electron (Sublattice) <./execution/execute_sublattice>`

:doc:`Choosing an Executor For a Task <./execution/choosing_executors>`

:doc:`Canceling a Workflow <./execution/cancel_dispatch>`

.. :doc:`Executing an Electron in a Conda Environment <./execution/choosing_conda_environments>`

:doc:`Adding a Time Trigger to a Lattice <./execution/trigger_time>`

:doc:`Adding a Directory Trigger to a Lattice <./execution/dir>`

:doc:`Canceling a Running Workflow <./execution/cancel_dispatch>`

.. _howto_querying:

Querying and Viewing
********************

:doc:`Querying the Status of a Lattice in a Notebook<./status/query_lattice_execution_status>`

:doc:`Querying the Status of an Electron<./status/query_electron_execution_status>`

:doc:`Querying Lattice Execution Time <./status/query_lattice_execution_time>`

:doc:`Querying Multiple Workflows (Lattices)<./collection/query_multiple_lattice_execution_results>`

:doc:`Getting Results of Previous Workflow Dispatches <./collection/query_lattice_execution_result>`

:doc:`Getting the Result of a Task (Electron) <./collection/query_electron_execution_result>`

.. _howto_config:

Configuration
*************

:doc:`Customizing the Configuration <./config/customization>`

----------------------------------

Is anything missing? Contribute a guide on `GitHub <https://github.com/AgnostiqHQ/covalent/issues>`_.
