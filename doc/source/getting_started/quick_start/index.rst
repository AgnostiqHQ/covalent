=================
:octicon:`stopwatch;1em;` Quick Start
=================

To quickly install Covalent and run a short demo, follow the four steps below.

.. admonition:: Before you start

   Ensure you are using a compatible OS and Python version. See the :doc:`Compatibility <./../compatibility>` page for supported Python versions and operating systems.

.. card:: 1. Use Pip to install the Covalent server and libraries locally.


    Type the following in a terminal window:

    .. code:: bash

        $ pip install covalent



.. card:: 2. Start the Covalent server.

    In the terminal window, type:

    .. code:: console

        $ covalent start
        Covalent server has started at http://localhost:48008


.. card:: 3. Run a workflow.

    Open a Jupyter notebook or Python console and run the following Python code:

    .. code:: python

      import covalent as ct

      # Construct manageable tasks out of functions
      # by adding the @ct.electron decorator
      @ct.electron
      def add(x, y):
         return x + y

      @ct.electron
      def multiply(x, y):
         return x*y

      # Note that electrons can be shipped to variety of compute
      # backends using executors, for example, "local" computer.
      # See below for other common executors.
      @ct.electron(executor="local")
      def divide(x, y):
         return x/y

      # Construct the workflow by stitching together
      # the electrons defined earlier in a function with
      # the @ct.lattice decorator
      @ct.lattice
      def workflow(x, y):
         r1 = add(x, y)
         r2 = [multiply(r1, y) for _ in range(4)]
         r3 = [divide(x, value) for value in r2]
         return r3

      # Dispatch the workflow
      dispatch_id = ct.dispatch(workflow)(1, 2)
      result = ct.get_result(dispatch_id)
      print(result)


.. card:: 4. View the workflow progress.

    Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

    .. image:: ./../../_static/qs_ui_queue.png
      :align: center

    Click on the dispatch ID to view the workflow graph:

    .. image:: ./../../_static/qs_ui_graph.png
        :align: center

    Note that the computed result is displayed in the Overview.


Commonly Used Features
######################

The following code snippets show the syntax for some of the most popular features within Covalent.  Use this as a quick reference, or navigate to further examples in the :doc:`How-To Guide <../../how_to/index>`.

Executors
*********

Executors are included in Electron and Lattice decorators to denote where tasks should run. Note that most plugins must be installed as separate Python packages.

.. card:: Slurm Executor

   The Slurm executor generates a batch submission script and interacts with the Slurm scheduler on the user's behalf.

   .. code:: python

      slurm = ct.executor.SlurmExecutor(
          username="user",
          address="cluster.hostname.net",
          ssh_key_file="~/.ssh/id_rsa",
          remote_workdir="/scratch/user",
          conda_env="covalent",
          options={
              "cpus-per-task": 32,
              "qos": "regular",
              "time": "00:30:00",
              "constraint": "cpu",
          },
      )

      @ct.electron(executor=slurm)
      def task():
          ...

.. card:: Azure Batch Executor

   The Azure Batch Executor containerizes and submits a task to a compute pool in an Azure Batch account.

   .. code:: python

      azure = ct.executor.AzureBatchExecutor(
          tenant_id="aad-tenant-id",
          client_id="service-principal-client-id",
          client_secret="service-principal-client-secret",
          batch_account_url="https://myaccount.az-region.batch.azure.com"
          storage_account_name="mystorage",
          pool_id="my-compute-pool-name",
          time_limit=300,
      )

      @ct.electron(executor=azure)
      def task():
          ...

.. card:: Amazon Braket Executor

   The Amazon Braket executor containerizes a hybrid quantum task and submits it to Amazon Braket Hybrid Jobs.

   .. code:: python

      braket = ct.executor.BraketExecutor(
          credentials="~/.aws/credentials",
          region="us-east-1",
          s3_bucket_name="my-bucket-name",
          ecr_repo_name="my-container-repository",
          braket_job_execution_role_name="my-iam-role-name",
          quantum_device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
          classical_device="ml.m5.large",
          storage=30,
          time_limit=900,
      )

      @ct.electron(executor=braket)
      def task():
          ...

File Transfers
**************

File transfers are often used to keep large data files close to the compute where they are used. Covalent supports transferring files to/from arbitrary servers using a generic `rsync` strategy, as well as to/from all of the major cloud storage options.

.. card:: rsync transfers

   rsync is a generic transfer strategy which uses SSH to authenticate to a remote server. Typically this is used to interact with NAS (Network Attached Storage) systems.


What to Do Next
###############

Read :doc:`First Experiment <../first_experiment/index>` for a more thorough discussion of the components of this simple workflow, including the important role of *executors*.

Read :doc:`Concepts <../../concepts/concepts>` gain a deeper understanding of how Covalent works.

See the :doc:`Tutorials <../../tutorials/tutorials>` to see how to apply Covalent to real-world machine learning problems in a variety of subject domains.

See the :doc:`API Reference <../../api/index>` for usage information on ``electron``, ``lattice``, and ready-to-use executors.

See :doc:`AWS Plugins <../../api/executors/awsplugins>` to see how you can specify an executor to run this example on an AWS node using only two more lines of code.
