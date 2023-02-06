(concept_sdk)=
# The Covalent SDK

The Covalent SDK exists to enable compute-intensive workloads, such as ML training and testing, to run as server-managed workflows. To accomplish this, the workload is broken down into tasks that are arranged in a workflow. The tasks and the workflow are Python functions decorated with Covalent's *electron* and *lattice* interfaces, respectively.


(electron)=

## Electron

The simplest unit of computational work in Covalent is a task, called an *electron*, created in the Covalent API by using the `@covalent.electron` decorator on a function.

In discussing object-oriented code, it's important to distinguish between classes and objects. Here are notational conventions used in this documentation:

{code}`Electron` (capital "E")

: The {doc}`Covalent API class <../api/electrons>` representing a computational task that can be run by a Covalent executor.

electron (lower-case "e")

: An object that is an instantiation of the {code}`Electron` class.

{code}`@covalent.electron`

: The decorator used to (1) turn a function into an electron; (2) wrap a function in an electron, and (3) instantiate an instance of {code}`Electron` containing the decorated function (all three descriptions are equivalent).

The {code}`@covalent.electron` decorator makes the function runnable in a Covalent executor. It does not change the function in any other way.

The function decorated with {code}`@covalent.electron` can be any Python function; however, it should be thought of, and operate as, a single task. Best practice is to write an electron with a single, well defined purpose; for example, performing a single tranformation of some input or writing or reading a record to a file or database.

Here is a simple electron that adds two numbers:

```{code-block} python

import covalent as ct

@ct.electron
def add(x, y):
    return x + y
```

An electron is a building block, from which you compose a {ref}`lattice<lattice>`.

```{image} ./images/simple_lattice.png
:align: center
:width: 400
```


(lattice)=

## Lattice

A runnable workflow in Covalent is called a *lattice*, created with the {code}`@covalent.lattice` decorator. Similarly to electrons, here are the notational conventions:

{code}`Lattice` (capital "L")

: The {doc}`Covalent API class <../api/lattice>` representing a workflow that can be run by a Covalent dispatcher.

{code}`lattice` (lower-case "l")

: An obect that is an instantiation of the {code}`Lattice` class.

{code}`@covalent.lattice`

: The decorator used to create a lattice by wrapping a function in the {code}`Lattice` class. (The three synonymous descriptions given for electron hold here as well.)

The function decorated with {code}`@covalent.lattice` must contain one or more electrons. The lattice is a *workflow*, a sequence of operations on one or more datasets instantiated in Python code.

For Covalent to work properly, the lattice must operate on data only by calling electrons. By "work properly," we mean "dispatch all tasks to executors." The flexibility and power of Covalent comes from the ability to assign and reassign tasks (electrons) to executors, which has two main advantages, *hardware independence* and *parallelization*.

Hardware indepdendence

: The task's code is decoupled from the details of the hardware it is run on.

Parallelization

: Independent tasks can be run in parallel on the same or different backends. Here, *indepedent* means that for any two tasks, their inputs are unaffected by each others' execution outcomes (that is, their outputs or side effects). The Covalent dispatcher can run independent electrons in parallel. For example, in the workflow structure shown below, electron 2 and electron 3 are executed in parallel.

```{image} ./images/parallel_lattice.png
:align: center
:width: 400
```

:::{note}
A function decorated as an electron behaves as a regular function unless called from within a lattice. Only when an electron is invoked from within a lattice is the electron code invoked to run the function in an executor.
:::

:::{admonition} Also note
When an electron is called from another electron, it is executed as a normal Python function. That is, the calling electron (if run in a lattice) is assigned to an executor, but the inner electron runs as part of the calling electron – it is not farmed out to its own executor.
:::

The example below illustrates this simple but powerful paradigm. The tasks are constructed first using the {code}`@covalent.electron` decorator, then the {code}`@covalent.lattice` decorator is applied on the workflow function that manages the tasks.

(ml-example)=

```{code-block} python

# ML example: electrons and lattice

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
```

Notice that all the data manipulation in the lattice is done by electrons. The {doc}`How-to Guide <../how-to/index>` contains articles on containing data manipulation within electrons.


(sublattice)=

## Sublattice

It is common practice to perform a nested set of experiments. For example, you design an experiment from a set of tasks defined as electrons. You construct the experiment as a lattice, then dispatch the experiment using some test parameters.

Now assume that you want to run a series of these experiments in parallel across a spectrum of input parameters. Covalent enables exactly this technique through the use of *sublattices*.

A sublattice is a lattice transformed into an electron by applying an electron decorator after applying the lattice decorator.

For example, the lattice {code}`experiment` defined below performs some experiment for a given set of parameters. To carry out a series of experiments for a range of parameters, you wrap the {code}`experiment` lattice with the {code}`@electron` decorator to construct the {code}`run_experiment` sublattice. (The example below explicitly calls {code}`electron` to wrap {code}`experiment` rather than using "@" notation. The result is the same.)

When {code}`run_experiment_suite` is dispatched for execution, it runs the experiment with an array of different input parameter sets. Since this arrangement meets the criteria for independence of the sublattices' inputs and outputs, Covalent executes the sublattices in parallel!

```python
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

run_experiment = ct.electron(experiment) # Construct a sublattice

@ct.lattice
def run_experiment_suite(**params):
    res = []
    for param in params:
        res.append(run_experiment(**params))
    return res
```

Conceptually, as shown in the figure below, executing a sublattice adds the constituent electrons to the {doc}`transport graph <server_concepts>`.

```{image} ./images/sublattice.png
:align: center
:width: 600
```

:::{note}
Don't confuse {code}`ct.electron(lattice)`, which creates a sublattice, with {code}`ct.lattice(electron)`, which is a workflow consisting of a single task.
:::


(dispatch)=

## Dispatch

You dispatch a workflow in your Python code using the Covalent {code}`dispatch()` function. For example, to dispatch the {code}`run_experiment` lattice in the {ref}`ML example <ml example>`:

```{code-block} python

# Send the run_experiment() lattice to the dispatch server
dispatch_id = ct.dispatch(run_experiment)(C=1.0, gamma=0.7)
```


(trigger)=

## Trigger

It so happens that sometimes you might have a pre-defined workflow which you might want to run automatically, subject to a certain event occurring. This is enabled in Covalent using something called a `Trigger`.

You can attach a `Trigger` object to a lattice and every time an event described in that `Trigger` occurs, it'll perform a `trigger` action which is to do a dispatch of the connected lattice.

This is especially useful if Covalent is used in the middle of your already existing pipeline instead of a user facing tool. For example, if say in your pipeline, you want to plot a graph of a csv file anytime it gets modified, you will be able to do so using Covalent. In this case the following are the keywords:

- “modified” → this is the event which should trigger the `Trigger` object and dispatch the workflow
- “plot a graph” → this part is the definition of the workflow
- “a csv file” → this is the part that the `Trigger` object will be watching for changes

Let's see how this works:

There are multiple ways you can start the covalent server in regards to how triggers are handled:

```{code-block} bash

# Starting the default way which starts with the triggers server endpoints as part of Covalent server
covalent start

# Starting the Covalent server without the trigger endpoints, thus in order to use triggers you will have
# either have to start the triggers server independently or manage the observe() method of triggers manually
covalent start --no-triggers

# Starting the standalone triggers server without Covalent, this is useful if your Covalent server
# is running on a different machine than the triggers server
covalent start --triggers-only
```

Let's say for the sake of simplicity, for this example, you have started Covalent the default way. Utility of the other ways, can be found in the section after this.

You can connect a `Trigger` object to a lattice as:

```{code-block} python
...
tr_object = TimeTrigger(5)

@ct.lattice(triggers=tr_object):
def my_workflow():
    ...
```

Now when you dispatch this lattice with `ct.dispatch` these are the key things that happen:
1. First run of the lattice is disabled, so Covalent only saves the lattice and generates a `dispatch_id` so that it can be referenced at a later point if required.
2. The `Trigger` object gets registered on the triggers server, which by default is the same as Covalent's server.
3. Upon registering, the `observe()` method of the trigger gets called which starts observing for any desired condition to be met which will in turn call the trigger's `trigger()` method. For example, in the above case, a `TimeTrigger` is used with a time gap of `5` seconds; so every 5 seconds the `trigger()` method will be called.
4. The `trigger()` method performs an automatic dispatch of the connected lattice (connected through the `dispatch_id` obtained earlier) and stores the newly obtained `dispatch_id`s. This is to have a connection between the "parent" `dispatch_id` and its subsequent "child" `dispatch_id`s.
5. If you want to stop this automatic dispatching from happening further, you can call the `ct.stop_triggers(d_id)` function with the parent dispatch id `d_id`.

Another case which might be useful here is let's say you want to attach a trigger to a workflow which has already been dispatched, and you only have access to its `dispatch_id`, then in that case you can do the following:

```{code-block} python
tr_object = TimeTrigger(10)
tr_object.lattice_dispatch_id = dispatch_id
tr_object.register()
```

This way of attaching a trigger is equivalent to the one mentioned before that but gives more degrees of freedom than before, for example, you can register the same trigger to multiple workflows by just repeating the last two lines for each of them.

### Possible custom scenarios

Even though this method seems a bit more verbose than the one mentioned before, it is ideal for a more customized scenario which might be more in line with your needs. For example, let's say there are 3 machines:- 2 remote servers and 1 client machine. `ServerA` is the one where Covalent is running without triggers support, `ServerB` where only the triggers server is running, and `Client` is the one where you are working from.

Let's say our workflow `my_workflow` has been dispatched to `ServerA` without any triggers. We can attach triggers to that workflow and register it with the triggers server quite easily as so:

```{code-block} python
trigger = TimeTrigger(30)

# Attaching dispatch id of `my_workflow` to the trigger
trigger.lattice_dispatch_id = dispatch_id

# Specifying the address of the dispatcher server
trigger.dispatcher_addr = "<ServerA_addr>"

# Specifying the address of the triggers server
trigger.triggers_server_addr = "<ServerB_addr>"

# Registering it to the triggers server
trigger.register()
```

And this will be sufficient for your workflow to get dispatched every 30 seconds due to this trigger.

Registering the trigger is also not a necessary condition for this to work. For example, let's say you have a server of your own (or a long running process), and you'd like to run the observation component of the trigger as part of your server, then inside that you can call `trigger.observe()` function, and it will start observing. Something like this:

```{code-block} python
trigger = TimeTrigger(2)
trigger.lattice_dispatch_id = dispatch_id
trigger.dispatch_addr = `<ServerA_addr>`

# And now start observing
trigger.observe()
```

Although, in this case make sure blocking/non-blocking nature of `trigger.observe()` is handled correctly. Like, you'd probably want to offload `trigger.observe()` to a separate thread in case its a blocking call so as to not block execution of other components of your server. This can be checked through the boolean attribute: `trigger.observe_blocks` of any trigger.
