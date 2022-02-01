*********
Concepts
*********

===========================================
What is Covalent?
===========================================

Covalent is a Pythonic workflow management tool that can be used to perform computations on advanced classical and quantum computing hardwares. To start, the user defines a workflow, or a set of interdependent tasks, using Covalent's electron and lattice decorators. An electron is a Python function that performs some granular task, while a lattice is a workflow that executes various tasks to accomplish a larger computation. Workflows can be run locally or dispatched to quantum and classical hardwares using custom executors. Running computationally intensive jobs on HPC and quantum hardware can be expensive, so users can construct, visualize, and execute the workflow locally first. Once a workflow is submitted to the dispatcher, the execution progress can be tracked in the Covalent UI. The user interface is useful not just for monitoring the execution progress of individual tasks, but it also shows users the workflow graph. The workflow graph is the visual representation of the tasks and their dependency relations, so users can better understand and communicate their computations at a conceptual level. Lastly, Covalent allows users to easily analyze, reuse, and share results of both individual tasks as well as the workflow as a whole, so that users can iterate faster and collaborate more easily.

Users may find Covalent useful for a variety of reasons:

Covalent...

* minimizes the need to learn new syntax. Once it has been installed, it is as easy as breaking your script into functions and attaching decorators.
* parallelizes mutually independent parts of workflows.
* provides an intuitive user interface to monitor workflows.
* allows users to view, modify and re-submit workflows directly within a Jupyter notebook.
* manages the results of your workflows. Whenever the workflow is modified, Covalent natively stores and saves the run of every experiment in a reproducible format.

In summary, Covalent is an easy-to-use workflow orchestration tool that makes deploying high performance computing jobs seamless. The browser-based user interface and the design of the package makes it extremely easy to track the status of the computations. Covalent has been designed so that it is very easy to modify or build on top of previous computational experiments.

Users interact with Covalent in four main ways:

* :ref:`Workflow construction<Workflow construction>`

* :ref:`Workflow execution<Workflow execution>`

* :ref:`Status polling<Workflow status polling>`

* :ref:`Results collection<Workflow result collection>`


.. _Workflow construction:

===========================================
Workflow construction
===========================================

Workflow construction is the process of taking a computational objective and breaking it up into tasks -- simple, atomic Python functions. Tasks are constructed using an :code:`electron` decorator on a Python function. A workflow is made up of several tasks and can be defined by attaching a :code:`lattice` decorator to a Python function comprised of tasks. A workflow can further be used as a task in another larger workflow by converting it into an electron. These structures are referred to as :ref:`sublattices<Sublattice>`.

.. _Electron:

~~~~~~~~~~~~~~~
Electron
~~~~~~~~~~~~~~~

A workflow is comprised of one or more tasks. Tasks are constructed using the :ref:`electron<electrons_api>` decorator, which transforms a Python function into an :code:`Electron` object. These are the building blocks for a lattice, as can be seen in the figure below.

.. image:: ./images/simple_lattice.png
  :width: 400
  :align: center

One reason to convert tasks into electrons is that Covalent can parallelize execution of independent electrons within a lattice. In other words, when the input parameters for two electrons are independent of the execution outcome of the other, the tasks are performed in parallel. For example, in the workflow structure shown below, Electron 2 and Electron 3 are executed in parallel.


.. image:: ./images/parallel_lattice.png
   :width: 400
   :align: center

Below, we see an example of an electron that simply adds two numbers.

.. code-block:: python
    :linenos:

    import covalent as ct

    @ct.electron
    def add(x, y):
        return x + y

Covalent's design ensures that a function decorated as an electron can still be called as a regular Python function. Only when an electron is invoked from within a lattice do the electron properties come into play. In other words, a function decorated as an electron behaves as a regular function unless called from within the context of a lattice.

.. note:: When an electron is invoked by another electron, it is executed as a normal Python function.


.. _Lattice:

~~~~~~~~~~~~~~
Lattice
~~~~~~~~~~~~~~

A workflow can be constructed by applying the :ref:`lattice<lattices_api>` decorator to a Python function composed of electrons. In the example shown below, we first construct tasks using the electron decorator, and then use the lattice decorator on the workflow function which manages the tasks.

.. code-block:: python
    :linenos:

    from numpy.random import permutation
    from sklearn import svm, datasets
    import covalent as ct

    @ct.electron
    def load_data():
        iris = datasets.load_iris()
        perm = permutation(iris.target.size)
        iris.data = iris.data[perm]
        iris.target = iris.target[perm]
        return iris.data, iris.target

    @ct.electron
    def train_svm(data, C, gamma):
        X, y = data
        clf = svm.SVC(C=C, gamma=gamma)
        clf.fit(X[90:], y[90:])
        return clf

    @ct.electron
    def score_svm(data, clf):
        X_test, y_test = data
        return clf.score(X_test[:90], y_test[:90])

    @ct.lattice
    def run_experiment(C=1.0, gamma=0.7):
        data = load_data()
        clf = train_svm(data=data, C=C, gamma=gamma)
        score = score_svm(data=data, clf=clf)
        return score

.. warning:: When constructing a workflow out of tasks, users should avoid object manipulation within the lattice outside of electrons.

Single-Task Workflows
---------------------

An electron can also be executed as a single-task workflow by attaching a lattice decorator on top.

.. image:: ./images/single_electron_lattice.png
   :width: 200
   :height: 125
   :align: center

.. code-block:: python
   :linenos:

   import covalent as ct

   @ct.lattice
   @ct.electron
   def add(x, y):
       return x + y

This type of behavior is useful when testing and debugging individual workflow components in a more controlled manner.

Working with Iterables
----------------------

When composing a workflow, passing a slice of an iterable returned by one electron as an input to another iterable is also supported by Covalent.

.. code-block:: python
    :linenos:

    @ct.lattice
    def workflow(**params):
        res_1 = electron_1(**params)
        res_2 = electron_2(res_1[0]) # Using an iterable data structure slice as an input parameter
        ...

Loops
-----

The following design pattern for deploying multiple experiments using the :code:`for` loop is encouraged (when possible) as shown in the code snippet below.

.. code-block:: python
    :linenos:

    @ct.electron
    def experiment(**params):
        ...

    @ct.lattice
    def run_experiment(**experiment_params):
        res = []
        for params in experiment_params:
            res.append(experiment(**params))
        return res

This ensures that the independent experiments are performed in parallel rather than sequentially.

Best Practices
--------------

There are a few best practices to highlight when working with lattices.

.. code-block:: python

    import pandas as pd

    @ct.electron
    def task_1():
        return {'a': 1, 'b': 2, 'c': 3}

    @ct.lattice
    def workflow():
        abc_dict = task_1()
        return pd.DataFrame.from_dict(abc_dict)

    res = workflow.dispatch_sync(a=1)

The code snippet above will not execute properly, since lattices are supposed to be used to construct the workflow and not manipulate the execution results of an electron. When :ref:`dispatch<Workflow dispatch>` is called, a :ref:`transport graph<Transport graph>` is built using the electrons as graph nodes. During construction, these electrons are not executed, but rather simply added to the transport graph; however, any non-electron is executed. In the example above, :code:`pd.DataFrame.from_dict()` (non-electron) is executed during construction while :code:`task_1` (electron) is not executed. This raises an error since the output of :code:`task_1` is not available to be used as an input for :code:`pd.DataFrame.from_dict()`.

The above example can be restructured using an extra electron to transform the dictionary into a dataframe.

.. code-block:: python

    import pandas as pd

    @ct.electron
    def task_1():
        return {'a': 1, 'b': 2, 'c': 3}

    @ct.electron
    def task_2(x_dict):
        return pd.DataFrame.from_dict(x_dict)

    @ct.lattice
    def workflow():
        abc_dict = task_1()
        return task_2(abc_dict)

    res = workflow.dispatch_sync(a=1)

However, lattices do support some basic parsing of electron outputs:

.. code-block:: python

    class TestClass:
        def __init__(self):
            self.test_value = 1234

    @ct.electron
    def task_1():
        return [3, TestClass(), 7], {"m": [x**2, x, [2, {"l": 5}]]}

    @ct.electron
    def task_2(var):
        return var ** 2

    @ct.lattice
    def workflow():
        a, b = task_1()

        res_a1 = task_2(a[0])
        res_b = task_2(b['m'][0])
        res_a2 = task_2(a[1].test_value)

        # The following are not yet supported:
        # for i in a: -> iterating over the values
        # len(a) -> getting the length
        # a[0] = 1 -> assigning a value

    res = workflow.dispatch_sync(a=1)

Note that while the lattice construction has some minor restrictions, as indicated through these examples, electrons can be constructed from any Python function.

.. _Sublattice:

~~~~~~~~~~~~~~
Sublattice
~~~~~~~~~~~~~~

A sublattice is a lattice transformed into an electron using an electron decorator after applying the lattice decorator.

Often, a user wants to perform a nested set of experiments. For example, a user designs an experiment from a set of tasks. They define the set of tasks using the electron decorator. Following that, the user constructs the experiment using the lattice decorator. The user then dispatches the experiment using some test parameters. Now, consider that the user wants to run a series of these experiments in parallel across a spectrum of inputs. Covalent is designed to allow exactly that behavior through the use of `sublattices`. For example, the lattice :code:`experiment` defined below performs some experiment for some given parameters. When the user is ready to carry out a series of experiments for a range of parameters, they can simply decorate the :code:`experiment` lattice with the electron decorator to construct the :code:`run_experiment` sublattice. When :code:`run_experiment_suite` is dispatched for execution, Covalent then executes the sublattices in parallel.

.. code-block:: python

    @ct.electron
    def task_1(**params):
        ...

    @ct.electron
    def task_2(**params):
        ...

    @ct.lattice
    def experiment(**params):
        a = task_1(**params)
        final_result = task_2(a)
        return final_result

    run_experiment = ct.electron(experiment) # Construct sublattice

    @ct.lattice
    def run_experiment_suite(**params):
        res = []
        for param in params:
            res.append(run_experiment(**params))
        return res


Conceptually, as shown in the figure below, executing a sublattice adds the constituent electrons to the transport graph.

.. image:: ./images/sublattice.png
   :width: 600
   :height: 400
   :align: center

.. note:: :code:`ct.electron(lattice)`, which creates a sublattice, should not be confused with :code:`ct.lattice(electron)`, which is a single task workflow.

Note that the user should not construct a sublattice using the following pattern:

.. code-block:: python

    @ct.electron
    @ct.lattice
    def workflow(**params):
        ...

The following pattern is how a sublattice should be constructed:

.. code-block:: python

    @ct.lattice
    def workflow(**params):
        ...

    workflow_sublattice = ct.electron(workflow)

.. _Transport graph:

~~~~~~~~~~~~~~~~
Transport graph
~~~~~~~~~~~~~~~~

After the workflow has been defined, and before it can be executed, one of the first steps performed by the dispatcher server is to construct a dependency graph of the tasks. This `directed acyclic graph` is referred to as the Transport Graph, which is constructed by sequentially inspecting the electrons used within the lattice. As each electron is reached, a corresponding node and its input-output relations are added to the transport graph. The user can visualize the transport graph in the Covalent UI. Furthermore, the graph contains information on :ref:`execution status<Workflow status polling>`, task definition, runtime, input parameters, and more. Below, we see an example of transport graph for a machine learning workflow as it appears in the Covalent UI.

.. image:: ./images/transport_graph.png
    :align: center
    :scale: 60 %

.. _Workflow execution:

===========================================
Workflow execution
===========================================

Once a workflow has been constructed, users can run it either locally or on classical and quantum hardwares using custom :ref:`executor<Executors>` plugins. Since the computational cost of HPC hardwares can be large, we recommend that users run the workflow locally to debug all possible issues, i.e., using the local executor. Once the user is confident with their workflow, it can be :ref:`dispatched<Workflow dispatch>` on the local machine or on cloud backends. After the workflow has been dispatched, a results directory is created where all the computational outputs are stored in a :ref:`result<Result>` object. Access to these result objects are facilitated by the Covalent :ref:`results manager<Result Manager>`.


.. _Workflow dispatch:

~~~~~~~~~~~~~~~~~~~~~~~
Workflow dispatch
~~~~~~~~~~~~~~~~~~~~~~~

Once a workflow has been constructed, it is dispatched to the Covalent dispatcher server. The local dispatcher server is managed using the :ref:`Covalent Command Line Interface<dispatcher_api>` tool (see also: :doc:`how-to guide <../../how_to/execution/covalent_cli>`). Userscan dispatch the job to the local executor or to one of the cloud executors. When a workflow has been successfully dispatched, a dispatch ID is generated. This ensures that the Jupyter notebook or script where the task was dispatched can now be closed. The Covalent UI server receives updates from the dispatcher server: it not only stores the dispatch IDs, but also the corresponding workflow definitions and parameters corresponding to the dispatched jobs. An example of a workflow dispatch is shown in the code snippet below.

.. code-block:: python
    :linenos:

    dispatch_id = ct.dispatch(run_experiment)(C=1.0, gamma=0.7)


Once the workflow has been submitted to the dispatcher, all the relevant workflow information, including execution status and results, are tagged with a unique dispatch ID. In other words, the workflow details and execution results are not tied to the initial workflow definition, but rather an instance of the workflow execution. Covalent is designed in this way so that the user can retrieve and analyze results at a later point in time.

.. _Executors:

~~~~~~~~~~~~~
Executors
~~~~~~~~~~~~~

An executor is responsible for taking a task and executing it in a certain place in a certain way. For example, the local executor invokes the task on the user's local computer. Users can define custom executors to make Covalent compatible with any remote backend system.

The workflow defined in the :ref:`lattice<Lattice>` subsection uses the electron decorator without passing any custom parameters. By default, a local executor is chosen. However, Covalent allows users to...

* use different executors for each electron.

* pass in custom executors to the dispatcher.

.. code-block:: python
    :linenos:

    @ct.electron(backend=quantum_executor)
    def task_1(**params):
        ...
        return val

    @ct.electron(backend=gpu_executor)
    def task_2(**params):
        ...
        return val

This feature is very important to Covalent since a user might want to break down their workflow according to compute requirements, where some of the tasks require quantum hardware, while others require CPUs or GPUs. This design choice allows us to send each electron to the appropriate hardware.

See the how-to guide on customizing the local executor :doc:`How to customize the executor <../../how_to/execution/choosing_executors>`. Covalent also allows users to build their own executor plugins by inheriting from the `BaseExecutor` class as shown below.

.. code-block:: python

    from covalent.executor import BaseExecutor


    class CustomExecutor(BaseExecutor):
        ...

A variety of interesting executors are coming soon!

.. _Workflow status polling:

===========================================
Workflow status polling
===========================================

Once a workflow has been dispatched, users will want to track the progress of the tasks. This can be viewed using the Covalent UI. The user can view the dependencies between the various electrons.

.. _Status:

~~~~~~~~~~~
Status
~~~~~~~~~~~

The progress of the electron execution can be tracked using the Covalent UI.

.. image:: ./images/status_check.png
    :align: center
    :scale: 65 %


The user can view the dependencies among the various electrons in addition to the execution status (running, completed, not started, failed, or cancelled). Additional information on how long each task has been running for, or the total execution time is also shown in the Covalent UI.

.. _Workflow result collection:

===========================================
Workflow result collection
===========================================

As soon as a workflow has been successfully submitted, a dispatch ID and a result object are created to store the outcome details. The dispatch ID uniquely identifies the result object. A list of dispatch IDs corresponding to previously submitted workflows can be easily viewed in the Covalent UI. As each task is terminated, either due to an error, cancellation, or successful completion, the :ref:`result<Result>` object is updated by the :ref:`result manager<Result manager>`.

.. _Result manager:

~~~~~~~~~~~~~~~~~~~~~
Result manager
~~~~~~~~~~~~~~~~~~~~~

The Covalent result manager is responsible for storing, updating, and retrieving the workflow result object. The philosophy behind the result manager is to separate the experiment outcomes from the workflow that was initially defined in some Jupyter notebook or Python script. This decoupling ensures that once the workflow has been dispatched, users can easily track the progress in the Covalent UI even without the original source code. This has the added benefit that experiment outcomes are safely stored regardless of any mishaps. The result object can be retrieved in the following way.

.. code-block:: python

    dispatch_id = ct.dispatch(workflow)(**params)
    result = ct.get_result(dispatch_id=dispatch_id, wait=False, results_dir='./results')

The result manager allows us to retrieve the result object even if the computations have not completed by setting the :code:`wait` parameter to :code:`False` as shown above.

.. _Result:

~~~~~~~~~~~~~
Result
~~~~~~~~~~~~~

The :ref:`result<results_api>` object contains all relevant details related to workflow execution outcomes. It further includes information to make each experiment entirely reproducible. In other words, the result object also stores information about the exact workflow instance, task and input parameter choices, as well as the final computational outputs. Some of the information stored in the result object includes...

* computation start and end time (see an :doc:`example<../../how_to/status/query_lattice_execution_time>`).
* computation status (see examples for :doc:`electrons<../../how_to/status/query_electron_execution_status>` and :doc:`lattices<../../how_to/status/query_lattice_execution_status>`).
* print statements inside electrons.
* metadata associated with each electron and with the lattice.

Below, we see an example of how to access the :code:`status` attribute of the result object to perform some analysis with the results once the workflow has been successfully executed.

.. code-block:: python

    # Check if result has been successfully computed
    if result.status:

        # Carry out analysis with results
        ...

We can, just as conveniently, access the details of the computational output of each task (:doc:`how-to guide <../../how_to/collection/query_multiple_lattice_execution_results>`) and the whole workflow (:doc:`how-to guide <../../how_to/collection/query_lattice_execution_result>`).
