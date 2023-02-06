(trigger)=

# Automate Repetitive Tasks with Triggers

`Triggers` are a powerful feature in Covalent that allow you to automate repetitive tasks and streamline your workflow. With Triggers, you can define a pre-defined set of steps that will run automatically every time a specific event occurs.

To use Triggers, you simply need to attach a Trigger object to a lattice. Then, every time the event described in the Trigger occurs, the connected lattice will perform a trigger action and dispatch the connected workflow. This makes it easy to automate processes, reducing the risk of human error and ensuring that your pipeline runs smoothly and efficiently.

For example, if you want to plot a graph of a CSV file every time it gets modified, you can use Covalent's Triggers to automate this process. The Trigger will be watching for changes to the CSV file, and every time the file is modified, it will trigger the workflow to plot a graph of the data.

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

You can attach a Trigger object to a lattice very simply as shown below:

```{code-block} python
...
tr_object = TimeTrigger(5)

@ct.lattice(triggers=tr_object):
def my_workflow():
    ...
```

Under the hood, once this is done and When you dispatch the lattice using `ct.dispatch`, the following events occur:

- The first run of the lattice is disabled, and Covalent only saves the lattice and generates a `dispatch_id` for reference later.
- The `Trigger` object is registered on the triggers server, which is the same as the Covalent server by default.
- Upon registration, the `observe()` method of the trigger is called, which starts observing for the desired condition to be met. In the example above, the `TimeTrigger` with a time gap of 5 seconds will call the `trigger()` method every 5 seconds.
- The `trigger()` method performs an automatic dispatch of the connected lattice using the dispatch_id` obtained earlier, and stores the newly obtained `dispatch_id`s for connections between the "parent" and subsequent "child" `dispatch_id`s.

Once a trigger is started, to stop the automatic dispatching when an event happens, you can call `ct.stop_triggers(dispatch_id)` with the parent dispatch id `dispatch_id`.


# Attaching a Trigger to a Dispatched Workflow

Another case which might be useful here is let's say you want to attach a trigger to a workflow which has already been dispatched, and you only have access to its dispatch_id, then in that case you can do the following:

```{code-block} python
tr_object = TimeTrigger(10)
tr_object.lattice_dispatch_id = dispatch_id
tr_object.register()
```

This way of attaching a trigger is equivalent to the one mentioned before, but gives more degrees of freedom. For example, you can register the same trigger to multiple workflows by just repeating the last two lines for each of them. This method also eliminates the need to design workflows with the trigger in mind, disentangling the trigger creation code from the actual workflow code. And in fact, since a trigger can be set post the workflow creation, this method can be used to attach a trigger from an entirely different Python process than the one where the workflow was created


## Attaching Triggers to Workflow on Remote Server

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


## Adding a Trigger without Registering it to Triggers Server

You can also run the observation component of a trigger as part of your own server, without registering it with the triggers server. For example, if you have a long-running process on a server, you can call the `trigger.observe()` function to start observing, as follows:

```{code-block} python
trigger = TimeTrigger(2)
trigger.lattice_dispatch_id = dispatch_id
trigger.dispatch_addr = `<ServerA_addr>`

# And now start observing
trigger.observe()
```

Keep in mind that it's important to handle the blocking/non-blocking nature of the `trigger.observe()` function correctly. If it's a blocking call, it's recommended to offload `trigger.observe()` to a separate thread so it doesn't block the execution of other components of your server. You can check if `trigger.observe()` is blocking by accessing the `trigger.observe_blocks` attribute of any trigger.

This becomes extremely useful to write custom triggers, for example to trigger workflows off email/slack messages. The ability to run `trigger.observe()` as part of your own server or process opens up a world of possibilities to integrate triggers into your workflow in a way that best suits your use case.