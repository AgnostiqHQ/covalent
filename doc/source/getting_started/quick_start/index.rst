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
          batch_account_url="https://myaccount.az-region.batch.azure.com",
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

File transfers are often used to keep large data files close to the compute where they are used. Covalent supports transferring files to/from arbitrary servers using a generic `Rsync` strategy, as well as to/from all of the major cloud storage options.

.. card:: Rsync transfers

   Rsync is a generic transfer strategy which uses SSH to authenticate to a remote server. Typically this is used to interact with NAS (Network Attached Storage) systems.

   .. code:: python

      rsync = ct.fs_strategies.Rsync(
          username="user",
          host="storage.address.com",
          private_key_path="~/.ssh/id_rsa",
      )

      input_file = ct.fs.TransferFromRemote(
          "file:///path/to/remote/input",
          "file:///path/to/local/input",
          strategy=rsync,
      )

      output_file = ct.fs.TransferToRemote(
          "file:///path/to/remote/output",
          "file:///path/to/local/output",
          strategy=rsync,
      )

      @ct.electron(files=[input_file, output_file])
      def task(files):
          # input_file can be accessed at /path/to/local/input
          # output_file should be written to /path/to/local/output
          ...

Software Dependencies
*********************

Covalent allows task dependencies to be specified in the task metadata. When a task runs, it first validates these dependencies are installed, or attempts to install them if they are missing.

.. card:: Pip Dependencies

   Pip dependencies allow users to specify Python packages which are managed by the Pip package-management system.

   .. code:: python

      deps = ct.DepsPip(packages=["numpy==1.25.0"])

      @ct.electron(deps_pip=deps)
      def task():
          import numpy
          ...

Workflow Triggers
*****************

Workflow triggers are used to run workflows on schedules or when various upstream events occur. These are popular for stream-based processing.

.. card:: Directory Triggers

   Directory triggers run workflows whenever files in a directory are created, deleted, modified, or moved.

   .. code:: python

      trigger = ct.triggers.DirTrigger(
          dir_path="/path/to/watch",
          event_names=["created", "modified"],
      )

      @ct.lattice(triggers=trigger)
      def task():
          ...

Dynamic Workflows
*****************

Dynamic workflows allow users to construct dynamic execution patterns based on the outputs of upstream tasks. Advanced users can use these to include conditional logic, to control the degree of parallelism, and to perform real-time scheduling.

.. card:: Conditional Workflow Logic

   Conditional logic includes if/else, for, and while statements.

   .. code:: python

      @ct.electron
      def is_odd(number):
          return number % 2

      @ct.electron
      def f():
          ...

      @ct.electron
      @ct.lattice
      def dynamic_sublattice(condition):
          x = 0
          if condition:
              x += f()
          return x

      @ct.lattice
      def workflow(input):
          return dynamic_sublattice(is_odd(input))


.. card:: Dynamic Parallelism

   Dynamic parallelism allows users to determine the number of parallel tasks in a workflow at runtime.

   .. code:: python

      @ct.electron
      def determine_num_nodes():
          ...

      @ct.electron
      def task():
          ...

      @ct.electron
      @ct.lattice
      def dynamic_sublattice(num_nodes):
          data = [task() for node in range(num_nodes)]
          return data

      @ct.lattice
      def workflow():
          num_nodes = determine_num_nodes()
          return dynamic_sublattice(num_nodes)

.. card:: Dynamic Hardware Selection

   Hardware selection at runtime allows users to pick resources within a compute backend at runtime. This can be useful when dynamically deciding to add hardware accelerators such as GPUs.

   .. code:: python

      @ct.electron
      def get_problem_size():
          ...

      def task():
          ...

      @ct.electron
      def schedule(problem_size, threshold):
          executor_args = {
              ...
              options={"time": "01:00:00"}
          }

          # Request a GPU for large computational problems
          if problem_size > threshold:
              executor_args["options"]["gres"] = "gpu:v100:1"
          else:
              executor_args["options"]["cpus-per-task"] = 4

          return ct.executor.SlurmExecutor(**executor_args)

      @ct.electron
      @ct.lattice
      def dynamic_sublattice(problem_size):
          threshold = 10 ** 6
          return ct.electron(
              task,
              executor=schedule(problem_size, threshold)
          )()

      @ct.lattice
      def workflow():
          problem_size = get_problem_size()
          return dynamic_sublattice(problem_size)

.. card:: Cloudbursting

   Cloudbursting is a form of dynamic workflow used in conjunction with multiple executors, where the scheduling decision is made at runtime.

   .. code:: python

      def task():
          ...

      electrons = {
          "slurm": ct.electron(task, executor=slurm),
          "azure": ct.electron(task, executor=azure),
      }

      @ct.electron
      def schedule(num_cpu):
          # Query remote backends for availability
          # Return either "slurm" or "azure"
          ...

      @ct.electron
      @ct.lattice
      def dynamic_sublattice(backend):
          return electrons[backend]()

      @ct.lattice
      def workflow(num_cpu):
          backend = schedule(num_cpu)
          return dynamic_sublattice(backend)


What to Do Next
###############

Read :doc:`First Experiment <../first_experiment/index>` for a more thorough discussion of the components of this simple workflow, including the important role of *executors*.

Read :doc:`Concepts <../../concepts/concepts>` gain a deeper understanding of how Covalent works.

See the :doc:`Tutorials <../../tutorials/tutorials>` to see how to apply Covalent to real-world machine learning problems in a variety of subject domains.

See the :doc:`API Reference <../../api/api>` for usage information on ``electron``, ``lattice``, and ready-to-use executors.

See :doc:`AWS Plugins <../../api/executors/awsplugins>` to see how you can specify an executor to run this example on an AWS node using only two more lines of code.
