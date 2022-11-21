.. _slurm_executor:

🔌 Slurm Executor
"""""""""""""""""""""""""""

Executing tasks (electrons) in a remote cluster via SLURM. This executor plugin interfaces Covalent with HPC systems managed by `Slurm <https://slurm.schedmd.com/documentation.html>`_. In order for workflows to be deployable, users must have SSH access to the Slurm login node, writable storage space on the remote filesystem, and permissions to submit jobs to Slurm.

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

    pip install covalent-slurm-plugin


The following shows an example of how a user might modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ to support Slurm:

.. code:: bash

   [executors.slurm]
   username = "user"
   address = "login.cluster.org"
   ssh_key_file = "/home/user/.ssh/id_rsa"
   remote_workdir = "/scratch/user"
   cache_dir = "/tmp/covalent"

   [executors.slurm.options]
   nodes = 1
   ntasks = 4
   cpus-per-task = 8
   constraint = "gpu"
   gpus = 4
   qos = "regular"

   [executors.slurm.srun_options]
   cpu_bind = "cores"
   gpus = 4
   gpu-bind = "single:1"

The first stanza describes default connection parameters for a user who is able to successfully connect to the Slurm login node using, for example

.. code:: bash
    
    `ssh -i /home/user/.ssh/id_rsa user@login.cluster.org`.

The second stanza describes default parameters for ``#SBATCH`` directives in a Slurm submit script. Similarly, the final stanza describes default parameters passed directly to ``srun``, which may be necessary in some use cases.

Accordingly, the example above generates a script with the following preamble,

.. code:: bash

   #!/bin/bash
   #SBATCH --nodes=1
   #SBATCH --ntasks=4
   #SBATCH --cpus-per-task=8
   #SBATCH --constraint=gpu
   #SBATCH --gpus=4
   #SBATCH --qos=regular

where the job is submitted with:

.. code:: bash

   srun --cpu_bind=cores --gpus=4 --gpu-bind=single:1

To use the configuration settings, an electron’s executor must be specified with a string argument, in this case:

.. code:: python

   import covalent as ct

   @ct.electron(executor="slurm")
   def my_task(x, y):
       return x + y

Alternatively, specifying a ``SlurmExecutor`` instance allows users customize behavior scoped to specific tasks. The ``prerun_commands`` parameter can be used here to provide a list of shell commands to execute before submitting the workflow. Similarly, the ``postrun_commands`` parameter takes a list of shell commands to execute *after* submitting the script. Finally, the ``srun_append`` parameter can be used to modify the call to ``srun`` that submits the workflow, by adding commands outside the scope of ``srun``\ ’s options.

An example of a custom executor instance is shown below:

.. code:: python

   executor = ct.executor.SlurmExecutor(
       remote_workdir="/scratch/user/experiment1",
       options={
           "nodes": 1,
           "cpus-per-task": 8,
           "qos": "regular"
       },
       srun_options={
           "slurmd-debug": 4,
           "cpu_bind": "cores"
       },
       srun_append="nsys profile --stats=true -t cuda --gpu-metrics-device=all",
       prerun_commands = [
           "module load package/1.2.3",
           "srun --ntasks-per-node 1 dcgmi profile --pause"
       ],
       postrun_commands = [
           "srun --ntasks-per-node 1 dcgmi profile --resume",
           "python ./path/to/my/post_process.py -j $SLURM_JOB_ID"
       ]
   )

   @ct.electron(executor=executor)
   def my_custom_task(x, y):
       return x + y

The executor example above corresponds to an ``sbatch`` script with the following sequence of commands:

.. code:: sh

   module load package/1.2.3  # load module
   srun --ntasks-per-node 1 dcgmi profile --pause  # pause hardware counter

   # run profiled workflow execution
   srun --slurmd-debug=4 --cpu_bind=cores \
   nsys profile --stats=true -t cuda --gpu-metrics-device=all \
   python /scratch/user/experiment1/workflow_script.py

   srun --ntasks-per-node 1 dcgmi profile --resume  # resume hardware counter
   python ./path/to/my/post_process.py -j $SLURM_JOB_ID  # do some post-processing


.. autoclass:: covalent.executor.SlurmExecutor
    :members:
    :inherited-members:
