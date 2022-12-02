#################
Covalent Services
#################

The Covalent server is a service that runs on your local machine or on a server. The service contains a *dispatcher* that analyzes workflows (lattices) and hands its component functions (electrons) off to executors. Each executor is an adaptor to a backend hardware resource. Covalent has a growing list of turn-key executors for common compute backends. If no executor exists yet for your compute platform, Covalent supports writing your own.

The examples that follow assume that the Covalent server is running lcoally. You start and manage the local server using the :ref:`Covalent command-line interface (CLI)<dispatcher_api>` tool. (See also :doc:`How-to Guide <../how_to/execution/covalent_cli>`.)

.. _Transport Graph:

Transport Graph
===============

Before executing the workflow, the dispatcher constructs a dependency graph of the tasks, called the *transport graph*. Transport graphs are *directed acyclic graphs*, which are commonly used as a model for workflows. In this model, the nodes of the graph represent tasks and the edges represent dependencies.

The dispatcher constructs the transport graph by sequentially inspecting the electrons used within the lattice. As each electron is examined, a corresponding node and its input-output relations are added to the transport graph. You can view the transport graph in the GUI.


.. _Workflow Dispatch:

Workflow Dispatch
=================

You dispatch a workflow in your Python code using the Covalent :code:`dispatch()` function, as shown in this example:

.. code-block:: python
    :linenos:

    dispatch_id = covalent.dispatch(run_experiment)(C=1.0, gamma=0.7)

In the example, the :code:`dispatch()` function sends the lattice named :code:`run_experiment` to the dispatcher.

The dispatcher ingests the workflow and generates a dispatch ID, then tags all information about the dispatched workflow with the dispatch ID. This information includes:
* The lattice definition
* Runtime parameters to the lattice
* Execution status
* Result output

... in short, everything about the instantiated workflow before, during, and after its execution. Every time you dispatch a workflow, all this information is saved and the process is executed on the server. This means that after the workflow is dispatched you can close the Jupyter notebook or console on which you ran the script. You can view information about the process in the :doc:`GUI <ui_concepts>`.

.. _Executors:

Executors
=========

An executor is responsible for taking a task – an electron – and executing it on a particular platform in a certain way. For example, the *local* executor invokes the task on your local computer. You can specify an executor as a parameter when you define an electron, or omit the parameter to use the default executor.

.. note:: It would be reasonable to expect that the local executor is the default, but it is not. Instead, the local dispatch server starts a local Dask cluster and, for any task not explicitly assigned an executor, queues the task to the Dask cluster. This is usually more efficient than native local execution for parallel tasks.

For example, consider one of the electrons defined in the :doc:`API Concepts <api_concepts>` Lattice description:

.. code-block:: python

   @ct.electron
   def score_svm(data, clf):
       X_test, y_test = data
       return clf.score(X_test[:90], y_test[:90])

The definition uses the electron decorator without an executor parameter. By default, the dispatcher uses the Dask executor for that electron.

.. note:: Covalent has executors for many backend platforms, but if you need an executor that does not yet exist, you can define a custom executors for any remote backend system. See the :doc:`API Reference <../api/executors/index>` for a list of executors.

Covalent enables you to break down your workflow by compute requirements. You can:
* Use a different executors for every electron
* Change the executor of an electron simply by changing a parameter
* Pass custom executors to the dispatcher

For example, you might need to compute one task on a quantum platform and a different task on a GPU cluster:

.. code-block:: python
    :linenos:

    @ct.electron(executor=quantum_executor)
    def task_1(**params):
        ...
        return val

    @ct.electron(executor=gpu_executor)
    def task_2(**params):
        ...
        return val

.. _Results:

Results
=======


.. _Workflow Result Collection:

Workflow Result Collection
==========================

Regardless of the eventual workflow outcome, a :code:`Result` object is created and associated with the :ref:`dispatch ID <Workflow Dispatch>`


A list of dispatch IDs corresponding to previously submitted workflows can be easily viewed in the Covalent UI. As each task is terminated, either due to an error, cancellation, or successful completion, the :ref:`result<Results>` object is updated by the :ref:`result manager<Result manager>`.

.. _Results:

Result Manager
--------------

The Covalent result manager is responsible for storing, updating, and retrieving the workflow result object. The philosophy behind the result manager is to separate the experiment outcomes from the workflow that was initially defined in a Jupyter notebook or Python script. This decoupling ensures that once the workflow has been dispatched, users can easily track the progress in the Covalent UI even without the original source code. This has the added benefit that experiment outcomes are safely stored regardless of any mishaps. The result object can be retrieved in the following way.

.. code-block:: python

    dispatch_id = ct.dispatch(workflow)(**params)
    result = ct.get_result(dispatch_id=dispatch_id, wait=False)

The result manager allows us to retrieve the result object even if the computations have not completed by setting the :code:`wait` parameter to :code:`False` as shown above.
