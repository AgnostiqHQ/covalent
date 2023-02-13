(basic_primitives)=
# Covalent Basics

This section briefly introduces the most important Python classes and functions of the Covalent SDK. These elements are key to how Covalent works.


(basic_primitives_electrons)=
## Electron

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
## Lattice

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
## Dispatch

You dispatch a workflow in your Python code using the Covalent {code}`dispatch()` function. For example, to dispatch the {code}`cart_dist` lattice in the {ref}`Cartesian distance example <cartes example>`:

```python
    ## Send the run_experiment() lattice to the dispatch server
    dispatch_id = ct.dispatch(cart_dist)(x=3, y=4)
```

The dispatch server sends individual tasks to {ref}`executors<basic_primitives_executor>`.

A workflow that has been dispatched once can then be redispatched using the {code}`covalent.redispatch()` command which allows:

1. Redefining particular tasks in the workflow.
2. Reusing previously executed results as much as possible.
3. Re-executing the workflow with different set of arguments.

For example, you can redefine {code}`sum_xy` to {code}`weighted_sum_xy` and redispatch the workflow while reusing the previously computed results, with:

```python
@ct.electron
def weighted_sum_xy(x, y):
    return 0.5 * (x + y)


redispatch_id = ct.redispatch(
    dispatch_id,
    replace_electrons={'sum_xy': weighted_sum_xy},
    reuse_previous_results=True
)()
```

.. note:: Redispatching does not allow altering function signatures.

For more on how the Covalent dispatcher analyzes and runs lattices, see {ref}`Workflow Dispatch` in {doc}`server_concepts`.


(basic_primitives_result)=
## Result

Covalent stores the dispatch information and result of every lattice computation in a {doc}`Result <../api/results>` object that can be viewed in the Covalent GUI.

You can view the Result object in your notebook with {code}`covalent.get_result()` function. For example, to view the Cartesian results, use:

```python

    ## Retrieve the Covalent Result object
    result = ct.get_result(dispatch_id=dispatch_id, wait=True)
```

For more on how the Covalent result manager saves and presents results, see {ref}`Results` in {doc}`server_concepts`.


(basic_primitives_executor)=
## Executor

An executor runs a single task on a particular compute resource such as your local machine or an AWS cluster. Depending on how a lattice is written, a dispatcher might execute many electrons in parallel on several executors. The default executor is a Dask cluster running on the Covalent server.

For more on Covalent executors and how they run tasks, see {ref}`Executors` in {doc}`server_concepts`.


## Sublattice

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
