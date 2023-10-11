(triggers)=

# Automate Repetitive Tasks with Triggers

Triggers are a powerful feature in Covalent that enable you to automate repetitive tasks and streamline your workflow. With triggers, you configure a workflow to run automatically every time a specific event occurs.

To use triggers, attach a {doc}`trigger <../api/triggers>` object to a workflow (`../api/lattice`). Then, every time the event described in the trigger occurs, the trigger dispatches the lattice.

For example, if you want to plot a graph of a CSV file every time the file is modified, you can use a trigger to automate that process. The trigger watches the CSV file for changes and runs the workflow to plot a graph of the data whenever it detects a change.

Triggers are especially useful if you're using Covalent as part of a larger pipeline, rather than as (or in addition to) a user-facing tool. By automating tasks, you can save time, reduce the risk of error, and ensure that your pipeline runs smoothly and efficiently.


## Starting the Trigger Server

The Covalent server can be run with or without the trigger server endpoints included, or as a standalone trigger server for remote workflows. The following Bash commands illustrate the three different start methods.

(triggers_default)=
By default, Covalent server runs the trigger server along with the dispatch service. To start the server, use the `covalent start` command on the command line (in a Bash shell, for example):

```{code-block} bash
# Default method: Start with the trigger server endpoints as part of the Covalent server.
covalent start
```

To start the Covalent server without the trigger server, for example if you know you're only going to trigger events remotely, use the `--no-triggers` option on the command line:

```{code-block} bash
# Start the Covalent server without the trigger endpoints. In this case, to use triggers you
# must start the trigger server independently or manage the trigger observe() method manually.
covalent start --no-triggers
```

Conversely, run the trigger server without the dispatch server with the `--triggers-only` option. This is the other half of a remote trigger setup:

```{code-block} bash
# Start the standalone trigger server without Covalent. Use when a Covalent server
# is running on a different machine than the trigger server.
covalent start --triggers-only
```

## Using Triggers

The rest of this page describes how invoke triggers under different trigger and dispatch server configurations.

### Using a Local Trigger

The simplest way to use a trigger is to call it on a combined dispatch/trigger server. The {ref}`default server configuration <triggers_default>` and default setting of the trigger's {ref}`internal functions flag<triggers_remote>` support this option, as demonstrated in the following two scenarios.


#### Attaching a Trigger at Workflow Creation

The following example implements a trigger on a combined Covalent dispatch and trigger server. Attach a {doc}`Trigger <../api/triggers>` object to a lattice as shown below:

```{code-block} python
...
tr_object = TimeTrigger(5)
@ct.lattice(triggers=tr_object):
def my_workflow():
    ...
```
When you dispatch the `my_workflow` lattice defined above using `ct.dispatch`, the following events occur:

1. The initial run of the lattice is disabled.
2. Covalent saves the lattice and generates a `dispatch_id` for later use.
3. The {doc}`Trigger <../api/triggers>` objects specified in the `triggers` parameter are registered on the trigger server (running on the Covalent server).

    ```{note}
    You can supply a single `trigger` object or a list of `trigger` objects to the `triggers` parameter.
    ```
4. Upon registration, the `observe()` method of the trigger is called. This starts an asynchronous observer waiting for the condition to be met. In this example, a {doc}`TimeTrigger <../api/triggers>` object with an interval of 5 seconds calls the `trigger()` method every 5 seconds.
5. `ct.dispatch` returns with the generated `dispatch_id`.
6. The `trigger()` method, when it is called, dispatches the associated lattice using the previously generated (parent) `dispatch_id`, and obtains a new (child) `dispatch_id`.


#### Attaching a Trigger to a Dispatched Workflow

Now assume you want to attach a trigger to a workflow that has already been dispatched, and that you know the workflow's `dispatch_id`. Create a trigger as shown below.

```{code-block} python
tr_object = TimeTrigger(10)
tr_object.lattice_dispatch_id = dispatch_id
tr_object.register()
```

This method of attaching a trigger is equivalent to the previous, but provides more flexibility. For example, you can register the same trigger to multiple workflows by just repeating the last two lines with each workflow's `dispatch_id`.

This method also eliminates the need to consider triggers when designing a workflow, decoupling the trigger creation code from the workflow code. And in fact, since a trigger can be set after workflow creation, this method can be used to attach a trigger from an entirely different Python process than the one where the workflow was created.

```{note}
If you know that you're going to attach a trigger to a workflow after it is dispatched and don't want to run the workflow on the first pass or until a trigger event takes place, then dispatch the workflow with:

`ct.dispatch(my_workflow, disable_run=True)()`

The dispatch won't run the workflow but will return a `dispatch_id` that you can use later.
```

### Using a Remote Trigger

When a trigger fires, it dispatches a workflow either by directly accessing the required Covalent server function or by calling the REST API endpoint at the server IP adress and port. Which of these two methods it uses is controlled by a flag, `use_internal_funcs`, in the `trigger` object.

(triggers_remote)=

In the default case, with the trigger running in the dispatch server process, the trigger directly accesses the internal dispatch function directly. In this case, `trigger.use_internal_funcs` is set to `True`. This is its default value.

When deployed remotely, a trigger must use the Covalent server's REST API endpoint to dispatch a workflow. In such cases (the two scenarios below), set `trigger.use_internal_funcs = False` to force the trigger to interact with the dispatch server through the API endpoints.

#### Attaching a Trigger to a Workflow on a Remote Server

To trigger a dispatched workflow from a separate host, provide the `dispatch_id` and the address of both the Covalent server and the trigger server.

For example, consider a scenario where there are three hosts: two remote servers and one client. Covalent is running on `ServerA` without trigger support; the trigger server (only) is running on`ServerB`; and `Client` is a client node.

Assume a workflow `my_workflow` has been dispatched on `ServerA` without any triggers. To attach triggers to the workflow and register it with the trigger server, follow the steps illustrated in the Python code below:

```{code-block} python
# 1. Create the trigger
trigger = TimeTrigger(30)

# 2. Set the trigger to interact with the dispatcher server through API endpoints
trigger.use_internal_funcs = False

# 3. Attach the dispatch ID of `my_workflow` to the trigger
trigger.lattice_dispatch_id = dispatch_id

# 4. Specify the address of the dispatcher server
trigger.dispatcher_addr = "<ServerA_addr>"

# 5. Specify the address of the trigger server
trigger.triggers_server_addr = "<ServerB_addr>"

# 6. Register the trigger with the trigger server
trigger.register()
```

Once this setup is complete, the trigger dispatches the workflow to the dispatch server every 30 seconds.


#### Adding a Trigger without Registering it to the Trigger Server

You can run the `observation` component of a trigger as part of your own server or application code, without registering it on the trigger server. For example, if you have a long-running process on a server, you can call the `trigger.observe()` function to activate the trigger:

```{code-block} python
trigger = TimeTrigger(2)
trigger.use_internal_funcs = False
trigger.lattice_dispatch_id = dispatch_id
trigger.dispatcher_addr = `<ServerA_addr>`

# Start observing
trigger.observe()
```

The `trigger.observe()` function can be called synchronously (blocking) or asynchronously (non-blocking). If you use `trigger.observe()` as a blocking call, we recommend that you run it on a separate thread so it doesn't block other components of your server. You can check if `trigger.observe()` is blocking by querying the trigger's `trigger.observe_blocks` attribute. The `trigger.observe()` funciton is especially useful when writing custom triggers, for example to trigger workflows on email or Slack messages.

For further examples of how to use triggers, see these articles in the How-to Guide:

## Types of Triggers in Covalent

Covalent offers an array of triggers designed to cater to diverse use cases, simplifying the automation of tasks based on a range of conditions. It's important to note that this list represents the currently available triggers, with more to be added in the future. If you find these triggers valuable and have suggestions for new ones, we encourage you to contribute to Covalent's GitHub repository.

Here are the currently available triggers in Covalent:

1. `DirTrigger`: This trigger observes a specified directory or file for events such as creation, deletion, modification, or movement. It performs the trigger action when these events occur. For example:

```{code-block} python
from covalent.triggers import DirTrigger
import covalent as ct

dir_trigger = DirTrigger(dir_path='path/to/your/directory', event_names=['modified'])

@ct.lattice(triggers=dir_trigger)
def my_workflow():
    ...
```

2. `TimeTrigger`: This trigger performs the trigger action after a specified time interval. It is useful for recurring tasks or periodic data processing. For example:

```{code-block} python
from covalent.triggers import TimeTrigger
import covalent as ct

time_trigger = TimeTrigger(time_gap=5)  # Trigger action every 5 seconds

@ct.lattice(triggers=time_trigger)
def my_workflow():
    ...
```


3. `SQLiteTrigger`: This trigger monitors an SQLite database for changes and performs the trigger action when changes occur. It is helpful for automating tasks in response to database updates. For example:

```{code-block} python
from covalent.triggers import SQLiteTrigger
import covalent as ct

sqlite_trigger = SQLiteTrigger(db_path='path/to/your/database.sqlite',table_name='your_table)

@ct.lattice(triggers=sqlite_trigger)
def my_workflow():
    ...

```


4. `DatabaseTrigger`: This trigger monitors the database for changes and performs the trigger action when changes occur. It is helpful for automating tasks in response to database updates. For example:

```{code-block} python
from covalent.triggers import DatabaseTrigger
import covalent as ct
database_trigger = DatabaseTrigger(db_path="db path",table_name='table name')
@ct.lattice(triggers=database_trigger)
def my_workflow():
    ...
```

These triggers can be easily integrated into your Covalent workflows to automate various tasks based on the desired conditions.

## Trigger How-to Guides

For further examples on how to use triggers, check out the Trigger how to guides:
- {doc}`How to add a directory trigger to a lattice <../../how_to/execution/trigger_dir>`
- {doc}`How to add a time trigger to a lattice <../../how_to/execution/trigger_time>`
- {doc}`How to add a sqlite trigger to a lattice <../../how_to/execution/trigger_sqlite>`
- {doc}`How to add a database trigger to a lattice <../../how_to/execution/trigger_database>`
