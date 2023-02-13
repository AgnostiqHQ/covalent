#########################
Deployment Best Practices
#########################

Although creating and dispatching workflows on a remote Covalent dispatcher is largely the same as with a local dispatcher, there are a few important differences.

The following sections explain some techniques for coding a workflow to run on a remote Covalent server that are not obvious at first.

Configuring the Client
----------------------

When Covalent is hosted remotely there is no need to run the Covalent server on a user's local (client) machine, but you do have to pass the dispatcher address and port to the workflow. There are three ways to do this:

* In the client-side configuration file
* Using ``set_config``
* In the ``dispatch`` and ``get_result`` methods


With the Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~~

On a client, when Covalent is imported it renders a `config` file that includes the dispatcher default address and port, ``localhost`` and ``48008``. Edit the ``dispatcher`` section of the client-side configuration, replacing the defaults with the remote values for the ``address`` and ``port``:

.. code:: bash

    [dispatcher]
    address = <remote covalent IP or hostname>
    port = <remote covalent port>
    ...

With set_config
~~~~~~~~~~~~~~~

The dispatcher ``address`` and ``port`` can be set using the ``set_config`` method before dispatching any workflows:

.. code:: python

    import covalent as ct

    ct.set_config({"dispatcher.address": "<dispatcher address>"})
    ct.set_config({"dispatcher.port": "<dispatcher port>"})

    ...

    dispatch_id = ct.dispatch(my_workflow)(*args, **kwargs)


With the dispatch and get_result Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify the dispatcher address and port directly in the ``ct.dispatch()`` and ``ct.get_result()`` functions:

.. code:: python

    import covalent as ct

    ...

    dispatch_id = ct.dispatch(workflow, dispatcher_addr="<addr>:<port>")(*args, **kwargs)
    result = ct.get_result(dispatch_id, dispatcher_addr="<addr>:<port>")


Assigning Executors
-------------------

In the context of a hosted Covalent server, there are three ways to specify an executor for an electron: server-side, client-side, and partially defined. (Partially-defined is a variation on the client-side executor, but is explained separately). All three ways of specifying executors have pros and cons.

Server-Side
~~~~~~~~~~~

In the server-side case, the client specifies only the short name of an executor on which to run an electron. The server constructs an instance of the named executor based on the configuration in its config file. The executor is constructed or recruited just in time for execution.

This is the best way to define executors when you want to manage the compute resources and executor specifications centrally.

.. code:: python

    import covalent as ct

    @ct.electron(executor="awsbatch")
    def task(*args, **kwargs):
    ...
    return result

Pros:

* Executor configuration and creation is centralized in one location, on the server.
* Clients don't need to know the details of executor implementation.

Cons:

* Clients are at the mercy of the server configuration.
* Executors have to be centrally managed and their names provided to clients.
* Executor configurations can be changed remotely through the Covalent GUI or by editing the configuration over SSH. This should be discouraged, or even prohibited, since the changes affect other clients' workflows without notifying them.


Client-Side
~~~~~~~~~~~

In the client-side case, the client passes a fully specified instance of the executor class to the remote dispatcher.

.. code:: python

    import covalent as ct

    awslambda = ct.executor.AWSLambdaExecutor(function_name="my-lambda-function", s3_bucket_name="my-s3-bucket-name")

    @ct.electron(executor=awslambda)
    def task(*args, **kwargs):
    ...
    return result

When a client passes a fully specified instance of an executor, the instance is pickled (serialized) for transport. The server deserializes the instance, then uses it to execute the task on the client-specified backend. In this case there is no ambiguity between the client and the server as to the executor parameters since all the values are specified by the client at workflow dispatch time.

Pros:

* There is no way the server can "surprise" the client by using a misdefined or redefined executor.
* The server does not need to supply executors to clients.

Cons:

* The submitter on the client side must ensure that the server has access to the executor resource. For example, if you require an ``AWSBatchExecutor`` in your workflows, then the remote Covalent server must have the proper IAM permissions and policies configured so that it can execute on your electron's behalf using the AWS Batch service.


Partially Defined
~~~~~~~~~~~~~~~~~

In this case, some parameter values are omitted from the executor's constructor. These omitted parameters are inferred from the client-side configuration during workflow construction, which occurs offline. The client does not interact with the dispatcher on the remote server until the workflow is submitted for execution.

.. code:: python

    import covalent as ct

    awsbatch = ct.executor.AWSBatchExecutor(vcpus=2)

    @ct.electron(executor=awsbatch)
    def task(*args, **kwargs):
    ...
    return result

From the server's perspective, this case is the same as the client-side executor: the executor is serialized for transport, and the server receives a fully specified instance. This case is broken out to emphasize that the client configuration can be exploited to "fill in" some of the executor parameters if they don't change for the particular client.


Stabilizing Dependencies
------------------------

By default, Covalent starts a local Dask cluster (the *default cluster*) on which it executes those tasks for which no executor is specified. This cluster by default runs in the same environment as Covalent and shares all the environment's Python packages.

Client-Side
~~~~~~~~~~~

Especially when Covalent is running on a server, we recommend that you avoid using ``DepsPip`` calls in your workflows. The client-requested ``pip`` packages are installed in the same environment as Covalent, potentially leading to unexpected package conflicts and destabilizing the Covalent server.

Server-Side
~~~~~~~~~~~

When hosting Covalent on a server, we recommend that you start a separate Dask cluster running either on an entirely different machine or in a separate virtual environment on the same machine. That way clients can share a Covalent virtual environment that is unmodified even if the workflows use frequent calls to ``DepsPip``.

.. note:: When running a separate Dask cluster on server-hosted Covalent, you must modify Covalent's server side configuration file to reflect the location of the Dask cluster.


Using LocalExecutor
-------------------

We recommend that you avoid using the ``LocalExecutor`` except for debugging purposes. Especially on a server, ``LocalExecutor`` is non-performant and potentially unstable.

Sharing Server Memory
---------------------

When submitting workflows to a hosted server, avoid constructing excessively large inputs and outputs for electrons. Remember that you're sharing a finite pool of memory with other clients.
