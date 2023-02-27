(cancel)=

# Canceling dispatches and tasks

Covalent users or admins may wish to cancel dispatches or individual tasks from a dispatch as per their requirements. For instance, under a self-hosted scenario if a dispatch has consumed more than the allocated cloud resources budget it should be canceled. Given that Covalent supports multi-cloud execution with its executor plugins, canceling a task involves the following actions

* Canceling tasks
  * Canceling a task may imply canceling the job being executed by a executor using remote cloud/on-prem resources
  * Interrupt the executor processing the job immediately. For instance, if a job's dependencies such as pickle callable, arguments and keyword arguments are uploaded but the backend has not yet started executing it, abort right away and do not provision any compute resources

* Canceling dispatches
    * When a dispatch is canceled, cancel all tasks that are part of the dispatch immediately. Any tasks currently being processed will be killed immediately and any unprocessed tasks will be abandoned.
    * Cancel all post-processing task

To cancel a dispatch, the UX is quite straightforward. To cancel an entire workflow, users only need to know the ``dispatch_id``. The following code snippet well illustrates the Covalent cancel API

```{code-block} python
   import covalent as ct

   dispatch_id = ct.dispatch(workflow)(args, kwargs)

   # cancel the workflow
   ct.cancel(dispatch_id)
```

Similarly to cancel a specific set of tasks within a single dispatch, users can invoke the `cancel` command as follows

```{code-block} python
import covalent as ct

# dispatch_id = ct.dispatch(workflow)(args, kwargs)

# Cancel tasks 1, 3, 5 from the above dispatch
ct.cancel(dispatch_id, task_ids=[1, 3, 5])
```

The effect of the above `cancel` command would be that it will interrupt or prevent tasks 1, 3 and 5 from running and all resources (local or remote) being consumed by these tasks will be released. Moreover, all subsequent electrons dependent on the outcomes of tasks 1, 3 and 5 will also not be executed.

```{note}
It is to be noted that if a node in a lattice is a **sub-lattice** then cancelling that particular node will recursively cancel all the sub tasks within that sub-lattice. Cancelling individual nodes from within a sub-lattice is not supported in Covalent since the transport graphs associated with sub-lattices are dynamically built at runtime
```
