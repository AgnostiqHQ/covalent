(redispatch)=

# Re-run previously dispatched workflows with Redispatch

The Redispatch feature allows users to re-run previously dispatched workflows and reuse as much of the previously executed workflow. A key property of this feature is that the redispatches only require the dispatch ID of the workflow that is being re-executed and does not need the workflow definition.

There are three aspect to redispatching that are discussed in more detail below:

1. Re-defining particular tasks in a workflow: Users can might want to run a workflow while using a different definition for a task. For example, a machine learning workflow with a postprocessing task might want to make changes.

2. Re-running a previously dispatched workflow with different input parameters without having access to the initial workflow definition.

3. While re-executing a workflow, users can chose the option of reusing previous results as much as possible.

```{warning}
The option of reusing previously computed results should not be exercised when there is stochasticity involved in a workflow.
```


## Redefining particular tasks in a workflow



```{note}
1. The function signature of the new task much match that of the old task.
2. If the new task is a sublattice, it will simply be treated as a regular function.
```


## Re-executing the workflow with different set of arguments


## Reuse previously executed results


## Redispatch How-to Guide

For further information on redispatching, checkout out the how-to guide:
- {doc}`Re-executing a workflow <../how_to/execution/redispatch>`
