*************************
Covalent Deployment Guide
*************************

Covalent supports both local and remote installation to suit different use cases. For quick prototyping and testing, running Covalent locally is sufficient.

For dispatching large compute-intensive workflows that require lots of CPU cores and memory, deploying Covalent as a *remote* server (cloud or on-premises) is better. Users can develop their workflows locally, then dispatch them to the remote Covalent server for execution.

.. image:: ./covalent-self-hosted.svg
   :width: 800
   :alt: Covalent self hosted deployment


Deployment with Docker
######################

Besides installing Covalent locally within a Python virtual environment, you can run Covalent as a Docker container using public images. Get the latest Docker image for Covalent with:

.. code:: bash

    docker pull public.ecr.aws/covalent/covalent:latest


.. note::  To get the current stable image of Covalent, use ``stable`` instead of ``latest``.

Start Covalent by running the container as follows:

.. code:: bash

    docker container run -d --name covalent -p 48008:48008 public.ecr.aws/covalent/covalent:latest

This starts the container in detached mode and forwards port ``48008`` to the host. To view the Covalent GUI, go to `http://localhost:48008 <http://localhost:48008>`_.

You can configure Covalent inside the container with environment variables.
The following table lists the environment variables available to customize Covalent's execution environment at startup:

.. list-table:: Covalent configuration environment variables
   :widths: 20 80
   :header-rows: 1

   * - Environment Variable
     - Description
   * - COVALENT_ROOT
     - Root directory for the ``covalent`` process
   * - COVALENT_CONFIG_DIR
     - Directory that ``covalent`` searches for its configuration file, ``covalent.conf``
   * - COVALENT_PLUGINS_DIR
     - Path where ``covalent`` looks to load any installed executor plugins
   * - COVALENT_DATABASE
     - Path to ``covalent``'s backend SQLite3 database
   * - COVALENT_LOGDIR
     - Path to ``covalent``'s log file
   * - COVALENT_CACHE_DIR
     - Directory used by ``covalent`` to store temporary objects during runtime
   * - COVALENT_DATA_DIR
     - Path to ``covalent``'s database directory
   * - COVALENT_RESULTS_DIR
     - Directory in which to store intermediate result objects
   * - COVALENT_SVC_PORT
     - TCP port on which ``covalent`` runs
   * - COVALENT_SERVER_IFACE_ANY
     - Boolean flag that causes ``covalent`` to listen on all network interfaces on the host
   * - COVALENT_NUM_WORKERS
     - Number of Dask workers in Covalent's default cluster
   * - COVALENT_MEM_PER_WORKER
     - Memory limit for each Dask worker
   * - COVALENT_THREADS_PER_WORKER
     - Number of threads with which to start each worker


For example, to start Covalent with two workers on port 8000:

.. code:: bash

   docker container run --name covalent -p 8000:8000 -e COVALENT_NUM_WORKERS=2 -e COVALENT_SVC_PORT=8000 public.ecr.aws/covalent/covalent:latest


On-Premises Deployment
######################

Create a centralized deployment by installing the Covalent server on an on-prem server or virtual machine. If the remote machine has `Docker <https://www.docker.com/>`_ enabled then the deployment amounts to simply pulling and running the Covalent container from our public registries. The deployment can be customized by following the steps outlined in :ref:`Deployment with Docker <Deployment with Docker>`.


Deployment with Systemd
-----------------------

There are several ways the Covalent server can be installed and managed as a `systemd <https://systemd.io/>`_ service. For example, you can directly install Covalent at the system level, install all the required plugins, create a ``covalent.service`` unit file, and enable the service.

.. warning::

   Installing Covalent at the system level is *not* recommended as its Python package dependencies can conflict with system packages. As well, the system Python version might not be compatible with Covalent. Refer to the :doc:`compatibility matrix <../getting_started/compatibility>` to see a list of supported Python versions.

To run Covalent under :code:`systemd`, we recommend that you create a Python virtual environment with Covalent installed and then run the :code:`systemd` service. This approach ensures that the system-level Python settings are unchanged and averts Python package dependency conflicts.

To install and run Covalent under :code:`systemd`


Deployment on AWS
#################

Users can deploy Covalent in their own AWS accounts with any ``x86`` based EC2 instance of their choice. Deploying on AWS cloud will allow users to vertically/horizontally scale up their deployments depending on their compute needs.

Similar to the Docker image, with each stable release, a ready to use Amazon Machine Image (AMI) is also released that is fully configured to start a Covalent server on instance boot. Users can query AWS Marketplace for the AMI ID directly from the console or via the ``aws cli`` command line tool.

.. code:: bash

   aws ec2 describe-images --owners Agnostiq --filter "Name=tag:Version,Values=0.202.0"

The above CLI example illustrates one can query details about the AMI released for version ``covalent==0.202.0``. Once the AMI id is retrieved, users can launch on EC2 instance in their account as follows

.. code:: bash

   aws ec2 run-instances --image-id <ami-id> --instance-type <instance-type> --subnet-id <subnet-id> -security-group-ids <security-group-id> --key-name <ec2-key-pair-name>

For more complicated deployments infrastructure as code tools such as `AWS CloudFormation <https://aws.amazon.com/cloudformation/>`_ or `Terraform <https://www.terraform.io/>`_ can be used.


Best Practices
##############

Self-hosting Covalent on remote machines is an easy way to run compute intensive workflows on machines other than a user's local workstation. Although the experience of creating and dispatching workflows is largely the same, there a few subtleties to consider.


Client/Server Side configuration
---------------------------------

When Covalent is deployed on remote machines Covalent parses all its configuration values from the configuration file it was deployed with i.e. **server side config**. The client side/local configuration file can be used by the client to set the dispatcher address and port information so that workflows can be dispatched to the remote server.

.. note::

   It is important to realize that when Covalent is hosted remotely there is no need for the Covalent server to be running on the user's local machine. Setting the server address and port in the user's local i.e. **client side** configuration file is enough for dispatching workflows

On the client side, when Covalent is imported it renders a `config` file based on its default values. Users can edit the ``dispatcher`` section of the client side configuration with the new values for the ``address`` and ``port``. These values default to ``localhost`` and ``48008`` on client side.

.. code:: bash

   [dispatcher]
   address = <remote covalent address/hostname>
   port = <remote covalent port>
   ...

The dispatcher ``address`` and ``port`` can also via the ``get_config`` method before dispatching any workflows

.. code:: python

   import covalent as ct

   ct.set_config({"dispatcher.address": "<dispatcher address>"})
   ct.set_config({"dispatcher.port": "<dispatcher port>"})

   ...

   dispatch_id = ct.dispatch(my_workflow)(*args, **kwargs)


Lastly, the dispatcher address can also be specified directly in the `ct.dispatch` and `ct.get_result` methods

.. code:: python

   import covalent as ct

   ...

   dispatch_id = ct.dispatch(workflow, dispatcher_addr="<addr>:<port>")(*args, **kwargs)
   result = ct.get_result(dispatch_id, dispatcher_addr="<addr>:<port>")


Executors
---------

When Covalent is deployed remotely, it is important to understand how ``executors`` are handled by the server. For instance, in Covalent there are multiple ways users can specify an ``executor`` for an electron in their workflows and each of the cases has certain implications on how the executor information is parsed and handled by the remote server

#. Using the executor short name

.. code:: python

   import covalent as ct

   @ct.electron(executor="awsbatch")
   def task(*args, **kwargs):
    ...
    return result

In this case, the server receives only the short name of the executor that ought to be used for executing the electron, thus the server will construct an instance of the specified executor using the configuration values specified in its config file i.e. **server side** during workflow execution just prior the the task being sent to the backend for execution. This is a very convenient way to choose executors in a workflow then the compute resources are being managed entirely by the remote server.

.. warning::

  Users however should be cautious of any changes being made to the **server side** configurations from the UI or directly over a SSH connection to the remote server.


#. Passing an instance of the executor class with fully specified input arguments

.. code:: python

   import covalent as ct

   awslambda = ct.executor.AWSLambdaExecutor(function_name="my-lambda-function", s3_bucket_name="my-s3-bucket-name")

   @ct.electron(executor=awslambda)
   def task(*args, **kwargs):
    ...
    return result

When a fully specified instance of an executor is passed to the remote server then the client passed instance is pickled and transported to the remote server, which then uses that to execute the task on the user specified backend. In this case there is not ambiguity between the client and the server as to which values of the executor ought to be parsed from the **server side** configuration file since all the values are specified by the client at workflow dispatch time.


.. warning::

   When providing executor information this way, users must ensure that the remote Covalent server has access to the executor backend. For instance, if the user is looking to use the ``AWSBatchExecutor`` in their workflows, then the remote Covalent server must have the proper IAM permissions and policies configured so that it can execute that task on the user's behalf using the AWS Batch service.


#. Passing an instance of an executor with partially specified input arguments

.. code:: python

   import covalent as ct

   awsbatch = ct.executor.AWSBatchExecutor(vcpus=2)

   @ct.electron(executor=awsbatch)
   def task(*args, **kwargs):
    ...
    return result

In this case, all the parameter values that are omitted from the executor's constructor are inferred from the **client side** configuration/environment during workflow construction time. This occurs offline and the dispatcher/remote server is not interacted with until the workflow is submitted for execution.


Environment Sanity
------------------

Covalent by default starts a local Dask cluster that it uses to execute tasks when executor metadata. This cluster by default runs in the same environment as Covalent and shares all the Python packages. In this case, users must be cautious of using any ``DepsPip`` call in their workflows as the user requested ``pip`` packages will be installed in the same environment as Covalent. This can potentially lead to unwarranted package conflicts and de-stabilize the Covalent server.

As a best practice, it is **recommended** that users start a separate Dask cluster that runs either on an entirely different machine or in a separate virtual environment on the same machine. This way users can ensure that Covalent's virtual environment will remain unmodified even if the workflows use frequent calls to ``DepsPip``.

.. note::

   When running a separate Dask cluster, users must make Covalent aware of the cluster's scheduler address and port by modifying the **server side** configuration file so that Covalent can submit tasks to it as they appear in the workflow


LocalExecutor & I/O
-------------------

For performance and stability reasons, users must avoid using the ``LocalExecutor`` as much as possible and only use it for debugging purposes. Secondly, users must aim to avoid excessively large inputs and outputs for their electrons as they can consume a lot of system memory.
