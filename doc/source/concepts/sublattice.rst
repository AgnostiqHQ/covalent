
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
