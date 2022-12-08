*************************************
:octicon:`mortar-board;1em;` Concepts
*************************************

This page is an introduction to the concepts that make Covalent unique as a workflow management system for machine learning experimentation. The page has two parts:

:ref:`Python Code Elements` introduces the functions and classes that are key to structuring experiments as workflows.

:ref:`Covalent Architecture` outlines the three main parts of the Covalent architecture and introduces the in-depth descriptions that follow:

    :doc:`api_concepts`
        Describes in more depth the Python code elements introduced below.

    :doc:`server_concepts`
        Describes in detail how the Covalent server handles workflows and dispatches tasks for execution.

    :doc:`ui_concepts`
        Shows how the Covalent GUI displays dispatched workflows in summary and detail forms, and how it saves and retrieves results.

.. _Python Code Elements:

Python Code Elements
--------------------

The most important conceptual elements in Covalent are implemented in a few Python objects and functions that you access from a single SDK module.

Electron
~~~~~~~~

The simplest unit of computational work in Covalent is a task, called an *electron*, created in the Covalent API by using the ``@covalent.electron`` decorator on a function.

The :code:`@covalent.electron` decorator makes the function runnable in a Covalent executor. It does not change the function in any other way.

Here is a simple electron that adds two numbers:

.. code-block:: python
    :linenos:

    import covalent as ct

    @ct.electron
    def add(x, y):
        return x + y

For more about tasks written as electrons, see :ref:`Electron` in :doc:`api_concepts`.


Lattice
~~~~~~~

A runnable workflow in Covalent is called a *lattice*, created with the :code:`@covalent.lattice` decorator. A workflow is a sequence of tasks. In Covalent, then, a lattice contains calls to one or more electrons.

The example below is a simple lattice. The tasks are constructed first using the :code:`@covalent.electron` decorator, then the :code:`@covalent.lattice` decorator is applied on the workflow function that manages the tasks.

.. _cartes example:

.. code-block:: python
    :linenos:

    # Cartesian example: electrons and lattice

    import covalent as ct
    import math

    @ct.electron
    def add(x, y):
        return x + y

    @ct.electron
    def square(x):
        return x**2

    @ct.electron
    def sqroot(x):
        return math.sqrt(x)

    @ct.lattice # Compute the Cartesian distance between two points in 2D
    def cart_dist(x=0, y=0):
        x2 = square(x)
        y2 = square(y)
        sum_xy = add(x2, y2)
        return sqroot(sum_xy)

Notice that all the data manipulation in the lattice is done by electrons. The :doc:`How-to Guide <../how-to/index>` has articles on containing data manipulation within electrons.

For more about workflows written as lattices, see :ref:`Lattice` in :doc:`api_concepts`.


Dispatch
~~~~~~~~

You dispatch a workflow in your Python code using the Covalent :code:`dispatch()` function. For example, to dispatch the :code:`cart_dist` lattice in the :ref:`Cartesian distance example <cartes example>`:

.. code-block:: python
    :linenos:

    # Send the run_experiment() lattice to the dispatch server
    dispatch_id = ct.dispatch(cart_dist)(x=3, y=4)

The dispatch server sends individual tasks to :ref:`executors<concept intro executor>`.

For more on how the Covalent dispatcher analyzes and runs lattices, see :ref:`Workflow Dispatch` in :doc:`server_concepts`.


Result
~~~~~~

Covalent stores the dispatch information and result of every lattice computation in a :doc:`Result <../api/results>` object that can be viewed in the Covalent GUI.

You can view the Result object in your notebook with :code:`covalent.get_result()` function. For example, to view the Cartesian results, use:

.. code-block:: python
    :linenos:

    # Retrieve the Covalent Result object
    result = ct.get_result(dispatch_id=dispatch_id, wait=True)

For more on how the Covalent result manager saves and presents results, see :ref:`Results` in :doc:`server_concepts`.


.. _concept intro executor:

Executor
~~~~~~~~


An executor runs a single task on a particular compute resource such as your local machine or an AWS cluster. Depending on how a lattice is written, a dispatcher might execute many electrons in parallel on several executors. The default executor is a Dask cluster running on the Covalent server.

For more on Covalent executors and how they run tasks, see :ref:`Executors` in :doc:`server_concepts`.


Sublattice
~~~~~~~~~~

A sublattice is a lattice transformed into an electron by applying an electron decorator after applying the lattice decorator.

For example, suppose you want to compute multiple Cartesian distances. You can package the :code:`cart_dist()` lattice as a sublattice, then call it just as you would an electron from another lattice:

.. code-block:: python
    :linenos:

    @ct.electron
    @ct.lattice # Compute the Cartesian distance between two points in 2D
    def cart_dist(x=0, y=0):
        x2 = square(x)
        y2 = square(y)
        sum_xy = add(x2, y2)
        return sqroot(sum_xy)

    def new_lattice(**kwargs):
      ...

For more about wrapping complex operations in sublattices, see :ref:`Sublattice` in :doc:`api_concepts`.


.. _Covalent Architecture:

Covalent Architecture
---------------------

Covalent consists of three component systems:

* A Python module containing an SDK that you use to build manageable workflows out of new or existing Python functions.
* A set of services that run locally or on a server to dispatch and execute workflow tasks.
* A browser-based UI from which to manage workflows and view results.

.. image:: ../_static/cova_archi.png
  :align: center

These components are briefly described below. A more detailed look at each component is presented in the following pages.


The Covalent SDK
~~~~~~~~~~~~~~~~

The Covalent API is a Python module containing a small collection of classes that implement server-based workflow management. The Covalent SDK is the subset of the API used to create and run workflows from Python code. The key elements are two decorators that wrap functions to create managed *tasks* and *workflows*.

The task decorator is called an *electron*. The electron decorator simply turns the function into a dispatchable task.

The workflow decorator is called a *lattice*. The lattice decorator turns a function composed of electrons into a manageable workflow.


Covalent Services
~~~~~~~~~~~~~~~~~

The Covalent server is a lightweight service that runs on your local machine or on a server. A dispatcher analyzes workflows (lattices) and hands its component functions (electrons) off to executors. Each executor is an adaptor to a backend hardware resource. Covalent has a growing list of turn-key executors for common compute backends. If no executor exists yet for your compute platform, Covalent provides base classes for writing your own.


The Covalent GUI
~~~~~~~~~~~~~~~~

The Covalent graphical user interface (GUI) is a browser-based dashboard displayed by the dispatch service. Covalent keeps a database of dispatched workflows, and the  GUI dashboard lists these dispatched workflows. From this list, you can select a single dispatched workflow and examine a graph and runtime details. You can also view logs, settings, and result sets.

.. toctree::
   :maxdepth: 1
   :hidden:

   api_concepts
   server_concepts
   ui_concepts
