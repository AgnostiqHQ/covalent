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
    conda_env = ""

    [executors.slurm.options]
    partition = "general"
    cpus-per-task = 4
    gres = "gpu:v100:4"
    exclusive = ""
    parsable = ""


The first stanza describes default connection parameters for a user who is able to successfully connect to the Slurm login node using :code:`ssh -i /home/user/.ssh/id_rsa user@login.cluster.org`. The second stanza describes default parameters which are used to construct a Slurm submit script. In this example, the submit script would contain the following preamble:

.. code:: bash

    #!/bin/bash
    #SBATCH --partition=general
    #SBATCH --cpus-per-task=4
    #SBATCH --gres=gpu:v100:4
    #SBATCH --exclusive
    #SBATCH --parsable


Within a workflow, users can then decorate electrons using these default settings:

.. code:: python

    import covalent as ct

    @ct.electron(executor="slurm")
    def my_task(x, y):
        return x + y


or use a class object to customize behavior scoped to specific tasks:

.. code:: python

    executor = ct.executor.SlurmExecutor(
        remote_workdir="/scratch/user/experiment1",
        conda_env="covalent",
        options={
            "partition": "compute",
        "cpus-per-task": 8
        }
    )

    @ct.electron(executor=executor)
    def my_custom_task(x, y):
        return x + y



.. autoclass:: covalent.executor.SlurmExecutor
    :members:
    :inherited-members: