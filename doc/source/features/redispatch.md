(redispatch)=

# Redispatching workflows with new task definitions and input parameters

The Redispatch feature allows users to re-run previously dispatched workflows with new input parameters and task definitions using only the dispatch ID, i.e. without access to the initial workflow definition. Furthermore, users have the option of skipping execution of previously computed tasks with the caveat that this should not be used when stochasticity or randomness in the workflow will affect the outcome.


## Redefining particular tasks in a workflow

Consider a workflow of the form:

```{code-block} python
import covalent as ct

@ct.electron
def load_data():
    ...


@ct.electron
def train_model(model_params, data):
    ...


@ct.electron
def compute_accuracy(model, test_data):
    ...


ct.lattice
def workflow(model_params):

    train_data, test_data = load_data()
    model = train_model(model_params, train_data)
    performance_metric = compute_accuracy(model, test_data)

    return model, performance_metric

# Dispatch the workflow.
dispatch_id = ct.dispatch(workflow)(
        model_params={C=1.0, gamma=0.7}
)
```

If the user wants to replace accuracy as a performance metric with recall, they can simply define a new performance metric task with the same function signature and then redispatch the workflow as follows:

```{code-block} python
@ct.electron
def compute_recall(model, test_data):
    ...

redispatch_id = ct.redispatch(
    dispatch_id,
    replace_electrons={"compute_accuracy": compute_recall}
)()
```

In the example above, no input arguments are provided in the redispatch function call parenthesis. In this case, the input arguments for the initial workflow dispatch are used by default.

```{note}
1. The function signature of the new task much match that of the old task.
2. If the new task definition is a sublattice, it will simply be treated as a task without the sublattice properties.
```

## Re-executing the workflow with new input arguments

In order to rerun the workflow defined above with new input parameters, users can pass the input parameters in the redispatch function call parenthesis as shown below.

```{code-block} python
# Case I - Recomputing the initial performance metric with new model parameters
redispatch_id = ct.redispatch(
    dispatch_id,
)(model_parameters={{C=1.0, gamma=0.7}})

# Case II - Recomputing the redefined performance metric with new model parameters
redispatch_id = ct.redispatch(
    dispatch_id,
    replace_electrons={"compute_accuracy": compute_recall}
)({C=1.0, gamma=0.7})
```

## Reuse previously computed results

Redispatch also has the option of reusing previously computed results. For example, if the user wants to replace the accuracy metric with recall as shown above without making any modifications to the training model parameters, they can do so as follows:


```{code-block} python
redispatch_id = ct.redispatch(
    dispatch_id,
    replace_electrons={"compute_accuracy": compute_recall},
    reuse_previous_results=True
)()
```

By default, the `reuse_previous_results` parameter is set to `False`.

```{warning}
It is important to ensure that reusing the previously computed results won't lead to erroneous results in workflows where stochasticity/randomness is involved.
```


## Redispatch How-to Guide

For further information on redispatching, checkout out the how-to guide:
- {doc}`Re-executing a workflow <../how_to/execution/redispatch>`
