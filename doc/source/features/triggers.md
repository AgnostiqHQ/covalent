(triggers)=

# Automate Repetitive Tasks with Triggers

Triggers are a powerful feature in Covalent that allow you to automate repetitive tasks and streamline your workflow. With these, you can define a pre-defined set of steps that will run automatically every time a specific event occurs.

To use Triggers, you simply need to attach a {doc}`Trigger <../api/triggers#covalent.triggers.BaseTrigger>` object to a lattice. Then, every time the event described in the trigger occurs, the connected lattice will perform a trigger action and dispatch the connected workflow. This makes it easy to automate processes, reducing the risk of human error and ensuring that your pipeline runs smoothly and efficiently.

For example, if you want to plot a graph of a CSV file every time it gets modified, you can use these Triggers to automate this process. The trigger will be watching the CSV file for changes, and every time the file is modified, it will run the workflow to plot a graph of the data.

Triggers are especially useful if you're using Covalent as part of a larger pipeline, rather than as a user-facing tool. By automating these tasks, you can save time, reduce the risk of error, and ensure that your pipeline runs smoothly and efficiently.




## Using Triggers

Covalent offers multiple options to start the server with regards to triggers. The default way starts the Covalent server with the triggers server endpoints included.

```{note}
It is also *possible* to start the Covalent server without the triggers endpoints and manage the `observe()` method manually, or start the standalone triggers server without Covalent.
```

The following code block showcases the three different start options:

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

For the purpose of this example, let's assume you started Covalent the default way.

You can attach a {doc}`Trigger <../api/triggers#covalent.triggers.BaseTrigger>` object to a lattice quite simply as shown below:

```{code-block} python
...
tr_object = TimeTrigger(5)

@ct.lattice(triggers=tr_object):
def my_workflow():
    ...
```

Under the hood, once this is done and when you dispatch the lattice using `ct.dispatch`, the following events occur:

- The first run of the lattice is disabled, and Covalent only saves the lattice and generates a `dispatch_id` for reference later.
- The {doc}`Trigger <../api/triggers#covalent.triggers.BaseTrigger>` object is registered on the triggers server, which is the same as the Covalent server by default.
- Upon registration, the `observe()` method of the trigger is called, which starts observing for the desired condition to be met in an unblocking manner. In the example above, the {doc}`TimeTrigger <../api/triggers#covalent.triggers.TimeTrigger>` with a time gap of 5 seconds will call the `trigger()` method every 5 seconds.
- At this point, `ct.dispatch` now returns with the earlier generate `dispatch_id`.
- The `trigger()` method, whenever it's called, performs an automatic dispatch of the connected lattice using the `dispatch_id` obtained earlier, and stores the newly obtained `dispatch_id`s for connections between the "parent" and subsequent "child" `dispatch_id`s.

Once a trigger is started, to stop the automatic dispatching when an event happens, you can call {doc}`ct.stop_triggers(dispatch_id) <../api/dispatcher#covalent.stop_triggers>` with the parent dispatch id `dispatch_id`.


## Attaching a Trigger to a Dispatched Workflow

Another case which might be useful here is let's say you want to attach a trigger to a workflow which has already been dispatched, and you only have access to its dispatch_id, then in that case you can do the following:

```{code-block} python
tr_object = TimeTrigger(10)
tr_object.lattice_dispatch_id = dispatch_id
tr_object.register()
```

This way of attaching a trigger is equivalent to the one mentioned before, but gives more degrees of freedom. For example, you can register the same trigger to multiple workflows by just repeating the last two lines for each of them. This method also eliminates the need to design workflows with the trigger in mind, disentangling the trigger creation code from the actual workflow code. And in fact, since a trigger can be set post the workflow creation, this method can be used to attach a trigger from an entirely different Python process than the one where the workflow was created

```{note}
In case you already know that you're gonna be attaching a trigger to a workflow post-dispatch and don't wish to run it the first time or until a trigger event takes place, then while dispatching it you can do `ct.dispatch(my_workflow, disable_run=True)()` and it won't start running but will still generate a `dispatch_id` which you can later use.
```


## Attaching Triggers to Workflow on Remote Servers

Another way to attach triggers to workflows that have already been dispatched is by utilizing the `dispatch_id` and the address of both the Covalent server and the triggers server. This is useful in scenarios where the trigger should be managed from a separate machine.

For example, let's consider a scenario where there are 3 machines: 2 remote servers and 1 client machine. `ServerA` is the one where Covalent is running without triggers support, `ServerB` where only the triggers server is running, and `Client` is the one where you are working from.

Let's say our workflow `my_workflow` has been dispatched to `ServerA` without any triggers. To attach triggers to that workflow and register it with the triggers server, you can follow the steps given below:

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


## Adding a Trigger without Registering it to the Triggers Server

You can also run the observation component of a trigger as part of your own server, without registering it with the triggers server. For example, if you have a long-running process on a server, you can call the `trigger.observe()` function to start observing, as follows:

```{code-block} python
trigger = TimeTrigger(2)
trigger.lattice_dispatch_id = dispatch_id
trigger.dispatch_addr = `<ServerA_addr>`

# And now start observing
trigger.observe()
```

Keep in mind that it's important to handle the blocking/non-blocking nature of the `trigger.observe()` function correctly. If it's a blocking call, it's recommended to offload `trigger.observe()` to a separate thread so it doesn't block the execution of other components of your server. You can check if `trigger.observe()` is blocking by accessing the `trigger.observe_blocks` attribute of any trigger.

This becomes extremely useful when writing custom triggers, for example to trigger workflows off of email/slack messages. The ability to run `trigger.observe()` as part of your own server or process opens up a world of possibilities to integrate triggers into your workflow in a way that best suits your use case.


For further examples on how to use triggers, check out the Trigger how to guides:
- {doc}`How to add a directory trigger to a lattice <../how_to/orchestration/dir_trigger>`
- {doc}`How to add a time trigger to a lattice <../how_to/orchestration/time_trigger>`
