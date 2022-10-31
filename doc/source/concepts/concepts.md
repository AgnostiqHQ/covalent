(concepts)=
# Concepts


This page is an introduction to the concepts that make Covalent unique as a workflow management system for machine learning experimentation. The page has two parts:



In the first part, we introduce the basic concepts that make up Covalent. These concepts are the building blocks of Covalent workflows.

:::::{grid} 4


::::{grid-item-card} `@ct.electron`
:link: basic_primitives_electrons
:link-type: ref
:img-top: images/electron.png

The smallest unit of computational task in covalent


::::

::::{grid-item-card} `@ct.lattice`
:link: basic_primitives_lattice
:link-type: ref
:img-top: images/lattice.png

Workflow constructor that strings together tasks

::::

::::{grid-item-card} `@ct.dispatch`
:link: basic_primitives_dispatch
:link-type: ref
:img-top: images/dispatch.png

Function to submit a workflow to the Covalent


::::

::::{grid-item-card} `@ct.get_result`
:link: basic_primitives_result
:link-type: ref
:img-top: images/get_result.png

Function to get the result of a workflow

::::

:::::



Next, {ref}`Covalent Architecture` outlines the three main parts of the Covalent architecture and introduces the in-depth descriptions that follow:

::::{grid} 3
:::{grid-item-card}  Covalent SDK
:link: architecture_sdk
:link-type: ref

Describes in more depth the Python code elements introduced below.
:::
:::{grid-item-card}  Covalent Server
:link: architecture_server
:link-type: ref

Describes in detail how the Covalent server handles workflows and dispatches tasks for execution.
:::
:::{grid-item-card}  Covalent GUI
:link: architecture_gui
:link-type: ref

Shows how the Covalent GUI displays dispatched workflows in summary and detail forms, and how it saves and retrieves results.
:::
::::


(basic_primitives)=
## Basics

This page is an introduction to the concepts that make Covalent unique as a workflow management system for machine learning experimentation. The page has two parts:

(basic_primitives_electrons)=
### Electron


The simplest unit of computational work in Covalent is a task, called an *electron*, created in the Covalent API by using the ``@covalent.electron`` decorator on a function.

The {code}`@covalent.electron` decorator makes the function runnable in a Covalent executor. It does not change the function in any other way.

Here is a simple electron that adds two numbers:

```python

    import covalent as ct

    @ct.electron
    def add(x, y):
        return x + y
```

For more about tasks written as electrons, see {ref}`Electron` in {doc}`api_concepts`.


(basic_primitives_lattice)=
### Lattice


A runnable workflow in Covalent is called a *lattice*, created with the {code}`@covalent.lattice` decorator. A workflow is a sequence of tasks. In Covalent, then, a lattice contains calls to one or more electrons.

The example below is a simple lattice. The tasks are constructed first using the {code}`@covalent.electron` decorator, then the {code}`@covalent.lattice` decorator is applied on the workflow function that manages the tasks.

(cartes example)=


```python
    ## Cartesian example: electrons and lattice

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

    @ct.lattice ## Compute the Cartesian distance between two points in 2D
    def cart_dist(x=0, y=0):
        x2 = square(x)
        y2 = square(y)
        sum_xy = add(x2, y2)
        return sqroot(sum_xy)

```

Notice that all the data manipulation in the lattice is done by electrons. The {doc}`How-to Guide <../how-to/index>` has articles on containing data manipulation within electrons.

For more about workflows written as lattices, see {ref}`Lattice` in {doc}`api_concepts`.


(basic_primitives_dispatch)=
### Dispatch

You dispatch a workflow in your Python code using the Covalent {code}`dispatch()` function. For example, to dispatch the {code}`cart_dist` lattice in the {ref}`Cartesian distance example <cartes example>`:

```python
    ## Send the run_experiment() lattice to the dispatch server
    dispatch_id = ct.dispatch(cart_dist)(x=3, y=4)
```

The dispatch server sends individual tasks to {ref}`executors<concept intro executor>`.

For more on how the Covalent dispatcher analyzes and runs lattices, see {ref}`Workflow Dispatch` in {doc}`server_concepts`.

(basic_primitives_result)=
### Result


Covalent stores the dispatch information and result of every lattice computation in a {doc}`Result <../api/results>` object that can be viewed in the Covalent GUI.

You can view the Result object in your notebook with {code}`covalent.get_result()` function. For example, to view the Cartesian results, use:

```python

    ## Retrieve the Covalent Result object
    result = ct.get_result(dispatch_id=dispatch_id, wait=True)
```

For more on how the Covalent result manager saves and presents results, see {ref}`Results` in {doc}`server_concepts`.


(concept intro executor)=

### Executor

An executor runs a single task on a particular compute resource such as your local machine or an AWS cluster. Depending on how a lattice is written, a dispatcher might execute many electrons in parallel on several executors. The default executor is a Dask cluster running on the Covalent server.

For more on Covalent executors and how they run tasks, see {ref}`Executors` in {doc}`server_concepts`.


### Sublattice


A sublattice is a lattice transformed into an electron by applying an electron decorator after applying the lattice decorator.

For example, suppose you want to compute multiple Cartesian distances. You can package the {code}`cart_dist()` lattice as a sublattice, then call it just as you would an electron from another lattice:

```python

    @ct.electron
    @ct.lattice ## Compute the Cartesian distance between two points in 2D
    def cart_dist(x=0, y=0):
        x2 = square(x)
        y2 = square(y)
        sum_xy = add(x2, y2)
        return sqroot(sum_xy)

    def new_lattice(**kwargs):
      ...
```

For more about wrapping complex operations in sublattices, see {ref}`Sublattice` in {doc}`api_concepts`.


(architecture)=
## Covalent Architecture


Covalent consists of three component systems:

- A Python module containing an SDK that you use to build manageable workflows out of new or existing Python functions.
- A set of services that run locally or on a server to dispatch and execute workflow tasks.
- A browser-based UI from which to manage workflows and view results.

```{eval-rst}
.. image:: ../_static/cova_archi.png
  :align: center
```

These components are briefly described below. A more detailed look at each component is presented in the following pages.


(architecture_sdk)=
### {ref}`concept_sdk`


The Covalent API is a Python module containing a small collection of classes that implement server-based workflow management. The Covalent SDK is the subset of the API used to create and run workflows from Python code. The key elements are two decorators that wrap functions to create managed *tasks* and *workflows*.

The task decorator is called an *electron*. The electron decorator simply turns the function into a dispatchable task.

The workflow decorator is called a *lattice*. The lattice decorator turns a function composed of electrons into a manageable workflow.

(architecture_server)=
### {ref}`concept_server`


The Covalent server is a lightweight service that runs on your local machine or on a server. A dispatcher analyzes workflows (lattices) and hands its component functions (electrons) off to executors. Each executor is an adaptor to a backend hardware resource. Covalent has a growing list of turn-key executors for common compute backends. If no executor exists yet for your compute platform, Covalent provides base classes for writing your own.


(architecture_gui)=
### The Covalent GUI


The Covalent graphical user interface (GUI) is a browser-based dashboard displayed by the dispatch service. Covalent keeps a database of dispatched workflows, and the  GUI dashboard lists these dispatched workflows. From this list, you can select a single dispatched workflow and examine a graph and runtime details. You can also view logs, settings, and result sets.


:::{toctree}
:maxdepth: 2
:hidden:

api_concepts
server_concepts
ui_concepts
