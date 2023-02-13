# Covalent Services

The Covalent server runs as a service on your local machine or on a server. The service contains a *dispatcher* that analyzes workflows (lattices) and hands its component functions (electrons) off to *executors*. Each executor is an adaptor to a backend hardware resource. Covalent has a growing list of turn-key executors for common compute backends. If no executor exists yet for your compute platform, Covalent provides base classes for writing your own.

The examples that follow assume that the Covalent server is running locally. You start and manage the local server using the {ref}`Covalent command-line interface (CLI)<dispatcher_api>` tool. (See also the {doc}`How-to Guide <../how_to/execution/covalent_cli>`.)


(transport-graph)=
## Transport Graph

Before executing the workflow, the dispatcher constructs a dependency graph of the tasks, called the *transport graph*. Transport graphs are *directed acyclic graphs*, which are a commonly used model for workflows. In this model, the nodes of the graph represent tasks and the edges represent dependencies.

The dispatcher constructs the transport graph by sequentially inspecting the electrons within the lattice. As each electron is examined, a corresponding node and its input-output relations are added to the transport graph. You can view the transport graph in the GUI.


(workflow-dispatch)=
## Workflow Dispatch

Recall that you dispatch a workflow in your Python code using the Covalent {code}`dispatch()` function:

```python
# Send the run_experiment() lattice to the dispatch server

dispatch_id = ct.dispatch(run_experiment)(C=1.0, gamma=0.7)
```

Often a workflow might need to be re-executed, with new parameters or updated task definitions. Furthermore, you might want to re-use as much of the previously executed results as possible. Given the {code}`dispatch_id`, the workflow can be redispatched using:

```python

# Redispatch the run_experiment lattice to the dispatch server with an updated svm training task definition.

redispatch_id = ct.redispatch(dispatch_id, replace_electrons={'train_svm': train_svm_redefined}, reuse_previous_results=True)()
```

The {code}`redispatch` command prepares the lattice and runtime parameters and triggers the {code}`dispatch` command.

The dispatcher ingests the workflow and generates a dispatch ID, then tags all information about the dispatched workflow with the dispatch ID. This information includes:
* The lattice definition
* Runtime parameters to the lattice
* Execution status
* Result output

... in short, everything about the instantiated workflow before, during, and after its execution. Every time you dispatch a workflow, all this information is saved and the process is executed on the server. This means that after the workflow is dispatched you can close the Jupyter notebook or console on which you ran the script. You can view information about the process in the {doc}`GUI <ui_concepts>`.


(executors)=
## Executors

An executor is responsible for taking a task – an {term}`electron` – and executing it on a particular platform in a certain way. For example, the *local* executor invokes the task on your local computer. You can specify an executor as a parameter when you define an electron, or omit the parameter to use the default executor.

:::{note}
It would be reasonable to expect that the local executor is the default, but it is not. Instead, the local dispatch server starts a local {term}`Dask` cluster and, for any task not explicitly assigned an executor, queues the task to the Dask cluster. This is usually more efficient than native local execution for parallel tasks.
:::

For example, consider one of the electrons defined in the {ref}`ML example <ml example>`:

```python
@ct.electron
def score_svm(data, clf):
    X_test, y_test = data
    return clf.score(X_test[:90], y_test[:90])
```

The definition uses the electron decorator without an executor parameter. By default, the dispatcher uses the Dask executor for that electron.

:::{note}
Covalent has executors for many backend platforms, but if you need an executor that does not yet exist, you can define a custom executors for any remote backend system. See {doc}`Executors <../api/executors/index>` in the {doc}`API Reference <../api/index>` for a list of executors.
:::

Covalent enables you to break down your workflow by compute requirements. You can:
* Use a different executors for every electron
* Change the executor of an electron simply by changing a parameter
* Pass custom executors to the dispatcher

For example, you might need to compute one task on a quantum platform and a different task on a GPU cluster:

```{code-block} python

@ct.electron(executor=quantum_executor)
def task_1(**params):
    ...
    return val

@ct.electron(executor=gpu_executor)
def task_2(**params):
    ...
    return val
```


(results)=
## Results

Covalent stores the result of every lattice computation in a {doc}`Result <../api/results>` object.

The {code}`Result` object contains not just the computed return value of the lattice function, but dispatch-related data including task and workflow times and durations, return statuses, and references to the lattice and parameters that generated the dispatch.


(workflow-result-collection)=
### Workflow Result Collection

Regardless of the eventual workflow outcome, a {code}`Result` object is created and associated with the {ref}`dispatch ID <Workflow Dispatch>` upon dispatch and is updated as tasks complete.

The Covalent UI provides a list of dispatched workflows. As each workflow task is terminated, either due to an error, cancellation, or successful completion, the {ref}`result<Results>` object is updated by the {ref}`result manager<Result manager>`.


(result-manager)=
### Result Manager

The Covalent server contains a Result Manager responsible for storing, updating, and retrieving workflow {code}`Result` objects. The Result Manager sits between the dispatched {code}`@lattice` and the {code}`Result` object, storing the experiment result and decoupling it from the workflow defined in a Jupyter notebook or Python script.

This decoupling ensures that once the workflow has been dispatched, updated outcomes are viewable in the Covalent UI even without the original source code. Partial outcomes are recorded at every task completion and are available thereafter, even in the event of a hardware failure or other mishap.

You can retrieve the result object even if the computations have not completed by setting the {code}`wait` parameter to {code}`False` as shown here:

```python
dispatch_id = ct.dispatch(workflow)(**params)
result = ct.get_result(dispatch_id=dispatch_id, wait=False)
```
