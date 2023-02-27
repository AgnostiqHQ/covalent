(cancel)=

# Canceling dispatches and tasks

Covalent users or admins may wish to cancel dispatches or individual tasks from a dispatch as per their requirements. For instance, under a self-hosted scenario if a dispatch has consumed more than the allocated cloud resources budget it should be canceled. Given that Covalent supports multi-cloud execution with its executor plugins, canceling a task involves the following actions

- Canceling tasks
  - Canceling a task may imply canceling the job being executed by a executor using remote cloud/on-prem resources
  - Interrupt the executor processing the job immediately. For instance, if a job's dependencies such as pickle callable, arguments and keyword arguments are uploaded but the backend has not yet started executing it, abort right away and do not provision any compute resources

- Canceling dispatches
    - When a dispatch is canceled, cancel all tasks that are part of the dispatch immediately. Any tasks currently being processed will be killed immediately and any unprocessed tasks will be abandoned.
    - Cancel all post-processing task

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

## Basic cancellation strategy

Covalent follows a very simple strategy to implement task/dispatch cancellation. Given that Covalent tasks are executed by various {doc}`executors <../api/executors/index>` canceling a node implies stopping the executor from executing the task any further if already running. Moreover, for Covalent to cancel a task a unique **job handle** assigned to that task by the executor is needed.

A **job handle** is typically assigned to the task when an executor beings processing it. Examples of unique **job handles** are as follows

- A `SLURM JOB ID` when the task is executed using the {doc}`SlurmExecutor <../api/executors/slurm>`
- A `AWS Batch` job id when the task is being executed by the {doc}`AWSBatchExecutor <../api/executors/awsbatch>`
- Job ARN when the {doc}`AWS Braket <../api/executors/awsbraket>` is used
- The Linux process ID when the task is executed using the {doc}`SSHExecutor <../api/executors/ssh>`

There is a convenient one to one mapping between tasks and their job handles that get uniquely assigned by the corresponding backends.

```{note}
In case of task packing when multiple electrons that use the same executor are packed and executed as a single task, this analogy gets modified from one-to-one to one-to-many
```

Once a unique `job handle` gets assigned by the remote backend for the task at hand, Covalent stores it in its local database for later retrieval and processing. Generally speaking the Covalent task ids i.e. electron id's in the transport graph map to a corresponding job handle that gets persisted in the database.

It is this `job handle` that gets used by Covalent when canceling individual tasks from a workflow. Executor plugins implement the necessary APIs to store the job handles and to cancel a task using it properly.


## Implications of canceling a task

Given that Covalent now supports cancellation of tasks at a node or at the lattice level, there are few caveats to be mindful off. A task decorated with a remote executor such as {doc}`AWSBatch <../api/executors/awsbatch>`, {doc}`Slurm <../api/executors/slurm>` etc carry out several steps prior to actually executing the electron code such as pickling the electron's `function`, `args` and `kwargs`, uploading the resulting pickle files to the remote destination be it an S3 bucket or the SLURM cluster's login node, provision compute resources, fetch the remote files etc. These are a few steps that generally speaking each remote executor in Covalent performs before successfully executing the dispatched task.

Now once a workflow is dispatched, Covalent starts processing it immediately. If a user then requests a particular node to be canceled, Covalent might be performing any of the aforementioned actions at the time the cancellation requests came in. Thus canceling a particular task implies the following in Covalent

- If the node has already started executing i.e the executor has already started running the electron's code, kill the job (SIGKILL/SIGTERM)
- If Covalent is yet to start processing a node, abort and do not attempt to process it
- If a node's function, args and kwargs are not pickled, do not pickle them and abort immediately
- If the required compute resources for the node have not yet been provisioned, do not provision them and abort immediately
- If Covalent has not instantiated the executor, do not instantiate an instance and abort immediately

```{note}
Cancelling a task in Covalent is treated as a hard **abort** and instructs Covalent to abandon processing the task any further
```
