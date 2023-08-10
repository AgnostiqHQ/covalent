(cancel)=

# Cancel with Confidence: Efficiently Manage Workflows in Covalent

Covalent offers the unique ability to cancel a workflow or any task in a workflow at any point before or during execution.

## Why Cancel?

Most ETL and workflow orchestrators focus solely on production workflows, with emphasis on automation, performance, and efficient management of business processes. Covalent was designed to support research-based as well as production workflows. Research workflows require the flexibility to accommodate modifications, including cancellation of running tasks.

Covalent's cancellation feature is indispensable in research workflow management, enabling you to stop any task or workflow that is taking too long to complete from consuming further resources. Covalent empowers you to confidently execute computation tasks on cutting-edge hardware platforms with high cost or limited availability, such as quantum computers, HPC clusters, GPU arrays, and cloud services, preventing budget and schedule overruns.

Besides stopping unneeded, over-long, and unnecessary jobs, the ability to cancel workflows or tasks encourages researchers and developers to modify their workflows to suit their changing needs, such as adjusting the computation pipeline or input data.

## How To Cancel a Task or Workflow

To cancel a dispatched workflow from a Python notebook or interactive environment, you issue a ``cancel`` directive with the ``dispatch_id`` of the workflow.

The following code illustrates how to use the Covalent ``cancel`` API.

```{code-block} python

 # In the notebook where you've dispatched the workflow ...
 import covalent as ct
 dispatch_id = ct.dispatch(workflow)(args, kwargs)

 # ... Do the following to cancel the workflow:
 ct.cancel(dispatch_id)
```

Similarly, to cancel a single task or a set of tasks within a single dispatch, use the same  `cancel` command, but  as follows:

```{code-block} python

# In the notebook where you've dispatched the workflow ...
import covalent as ct
dispatch_id = ct.dispatch(workflow)(args, kwargs)

# ... to cancel tasks 1, 3, and 5, for example:
ct.cancel(dispatch_id, task_ids=[1, 3, 5])
```

The `cancel` command interrupts or prevents tasks 1, 3, and 5. All resources (local and remote) being consumed by these tasks are released. Subsequent electrons dependent on the outcomes of tasks 1, 3, and 5 (that is, downstream in the transport graph) are also canceled and will not execute.

```{note}
If a node in a lattice is a *sublattice*, then cancelling that node recursively cancels all the tasks within the sublattice. Cancelling individual nodes within a sublattice is not supported in Covalent because the transport graphs associated with sublattices are dynamically built at runtime.
```

For complete examples of cancelling a task or workflow, see the {doc}`How-to guides <../how_to/index>`.

## How Task Cancellation Works

Recall that Covalent tasks (``@electrons``) are executed by various {doc}`executors <../api/executors/index>`. If the task is already running, cancelling it involves stopping the task's process, thread, or program on the resource fronted by the executor.

An executor assigns a unique **job handle** to a task when the executor begins processing it. The **job handle** identifies the compute resource and the ID assigned by the compute resource. Some examples are:

| Covalent Executor    | Compute Resource ID |
|----                  |----            |
| `SlurmExecutor`      | `SLURM JOB ID` |
| `AWSBatchExecutor`   | `AWS Batch` Job ID |
|  AWS `BraketExecutor`| Job Amazon Resource Name (ARN) |
| `SSHExecutor`        | Linux process ID |

Using the compute resource and resource-specific ID, the job handle uniquely identifies each task. Of course, tasks that have not yet been started do not yet have a job handle.

```{note}
In case of task packing when multiple electrons that use the same executor are packed and executed as a single task, the job handle-to-task relationship is not one-to-one but one-to-many.
```

Once a unique job handle is assigned to a task, Covalent stores it in its local database for later retrieval and processing. Covalent uses this job handle to cancel the individual task in a workflow. The executor plugin implements the necessary APIs to map the job handle to a process on a compute resource and use that information to stop the task process.


### How It Works in Even More Detail

A task decorated with a remote executor such as {doc}`AWSBatch <../api/executors/awsbatch>` or {doc}`Slurm <../api/executors/slurm>` carries out several steps before executing the electron code, including:

1. pickling the electron's `function`, `args`, and `kwargs`
2. uploading the resulting pickle files to the remote destination
3. provisioning compute resources
4. fetching remote files

Once a workflow is dispatched, if you then request a particular node be canceled, Covalent might be performing any of these preliminary actions when the cancellation request comes in. In general, Covalent stops at the earliest possible point in the process, doing no more processing of any kind on the task once it receives the cancellation request.

| If ... | Then Covalent ... |
|---- |---- |
| The node has already started executing (the executor has already started running the electron's code)| Kills the job (using SIGKILL/SIGTERM, for example) |
| Covalent has not yet begun executing the task | Aborts and does not attempt to process it |
| A node's function, `args` and `kwargs` are not pickled | Does not pickle them; aborts immediately |
| The required compute resources for the node have not yet been provisioned | Does not provision them; aborts immediately |
| Covalent has not instantiated the executor | Does not instantiate an instance; aborts immediately |

```{warning}
Cancelling a task in Covalent is treated as a hard **abort** and instructs Covalent to abandon processing the task any further.
```

To abort a task as early as possible, Covalent needs to poll for cancellation requests. When a cancellation is requested, Covalent asynchronously updates its database record for the canceled task, setting its Boolean `cancel_requested` flag to `True`. (This flag defaults to `False` for each node when it is created.)

Covalent's task execution process checks this flag before each of the steps named above.

### Implications for Custom Executors

Executor plugin developers can check the `cancel_requested` flag before each step, such as uploading pickled object to remote object stores, provisioning compute resources, executing the task, and so on. If an executor finds that the `cancel_requested` flag has been set to `True` for a task, it should raise a `TaskCancelledError` exception, which Covalent then handles to abort processing the task any further.


 To support task cancellation, an executor plugin must override the `cancel` method provided in the base executor class. This method has the following function signature:

```{code-block} python
def cancel(self, task_metadata: Dict, job_handle: str):
	...
```

The metadata associated with a task, `dispatch_id` and `node_id`, and the task's job handle are provided as inputs to the `cancel()` method. Use these inputs to implement the logic and backend-specific API calls to cancel the running task.


For examples of how to cancel workflows and individual tasks, refer to the {doc}`How-to guides <../how_to/index>`.
