===========================================
Components
===========================================

A Workflow has computational objective and can be broken up into tasks -- simple, atomic Python functions. Tasks are constructed using an :code:`electron` decorator on a Python function. A workflow is made up of several tasks and can be defined by attaching a :code:`lattice` decorator to a Python function comprised of tasks. A workflow can further be used as a task in another larger workflow by converting it into an electron. These structures are referred to as :doc:`Sublattice<sublattice>`. This step is kown as the Workflow construction.

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

Waiting for other electrons
----------------------

Covalent normally infers the dependencies between electrons from
their inputs and ouputs. Sometimes the user might want to wait for a
task's execution before executing another task even when the output of
one is not the input of another. The `wait()` function can be
handy in those cases.

.. code-block:: python
    :linenos:

    @ct.electron
    def task_1a(a):
        return a ** 2

    @ct.electron
    def task_1b(a):
        return a ** 3

    @ct.electron
    def task_1c(a):
        return a ** 4

    @ct.electron
    def task_2(x, y):
        return x * y

    @ct.electron
    def task_3(b):
        return b ** 3

    @ct.lattice
    def workflow():
        res_1a = task_1a(2)
        res_1b = task_1b(2)
        res_1c = task_1c(2)
        res_2 = task_2(res_1a, 3)
        res_3 = task_3(5)
	ct.wait(child=res_3, parents=[res_1a, res_1b, res_1c])

        return task_2(res_2, res_3)
        ...

    res = ct.dispatch_sync(workflow)()

The `wait()` statement instructs Covalent to wait for `task_1a`, `task_1b`, and `task_1c` to finish before dispatching `task_3`.


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

    res = ct.dispatch_sync(workflow)(a=1)

The code snippet above will not execute properly, since lattices are supposed to be used to construct the workflow and not manipulate the execution results of an electron. When :ref:`dispatch<Workflow dispatch>` is called, a :doc:`Transport graphs<transportGraph>` is built using the electrons as graph nodes. During construction, these electrons are not executed, but rather simply added to the transport graph; however, any non-electron is executed. In the example above, :code:`pd.DataFrame.from_dict()` (non-electron) is executed during construction while :code:`task_1` (electron) is not executed. This raises an error since the output of :code:`task_1` is not available to be used as an input for :code:`pd.DataFrame.from_dict()`.

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

    res = ct.dispatch_sync(workflow)(a=1)

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

    res = ct.dispatch_sync(workflow)(a=1)

Note that while the lattice construction has some minor restrictions, as indicated through these examples, electrons can be constructed from any Python function.



Other related documentation:

* :doc:`Sublattice<sublattice>`: A lattice transformed into an electron using an electron decorator after applying the lattice decorator.
* :doc:`Transport graphs<transportGraph>`: A directed acyclic graph with the dependency of the tasks.
* :doc:`Electron dependencies <electronDependencies>`:  One can specify different types of dependencies in an electron which will be installed or executed in the electron's backend execution environment.
