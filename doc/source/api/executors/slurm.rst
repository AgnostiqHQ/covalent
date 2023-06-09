.. _slurm_executor:

Slurm Executor
"""""""""""""""""""""""""""

This executor plugin interfaces Covalent with HPC systems managed by `Slurm <https://slurm.schedmd.com/documentation.html>`_. For workflows to be deployable, users must have SSH access to the Slurm login node, writable storage space on the remote filesystem, and permissions to submit jobs to Slurm.

Installation
============

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

    pip install covalent-slurm-plugin

On the remote system, the Python version in the environment you plan to use must match that used when dispatching the calculations. Additionally, the remote system's Python environment must have the base covalent package installed (e.g. :code:`pip install covalent`).

Usage
=====

Basics
------

The following shows an example of a Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ that is modified to support Slurm:

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

The first stanza describes default connection parameters for a user who can connect to the Slurm login node using, for example:

.. code:: bash

    ssh -i /home/user/.ssh/id_rsa user@login.cluster.org

The second and third stanzas describe default parameters for ``#SBATCH`` directives and default parameters passed directly to ``srun``, respectively.

This example generates a script containing the following preamble:

.. code:: bash

   #!/bin/bash
   #SBATCH --nodes=1
   #SBATCH --ntasks=4
   #SBATCH --cpus-per-task=8
   #SBATCH --constraint=gpu
   #SBATCH --gpus=4
   #SBATCH --qos=regular

and subsequent workflow submission with:

.. code:: bash

   srun --cpu_bind=cores --gpus=4 --gpu-bind=single:1

To use the configuration settings, an electron’s executor must be specified with a string argument, in this case:

.. code:: python

   import covalent as ct

   @ct.electron(executor="slurm")
   def my_task(x, y):
       return x + y

Pre- and Postrun Commands
------------------------

Alternatively, passing a ``SlurmExecutor`` instance enables custom behavior scoped to specific tasks. Here, the executor's ``prerun_commands`` and ``postrun_commands`` parameters can be used to list shell commands to be executed before and after submitting the workflow. These may include any additional ``srun`` commands apart from workflow submission. Commands can also be nested inside the submission call to ``srun`` by using the ``srun_append`` parameter.

More complex jobs can be crafted by using these optional parameters. For example, the instance below runs a job that accesses CPU and GPU resources on a single node, while profiling GPU usage via ``nsys`` and issuing complementary commands that pause/resume the central hardware counter.

.. code:: python

   executor = ct.executor.SlurmExecutor(
       remote_workdir="/scratch/user/experiment1",
       options={
           "qos": "regular",
           "time": "01:30:00",
           "nodes": 1,
           "constraint": "gpu",
       },
       prerun_commands=[
           "module load package/1.2.3",
           "srun --ntasks-per-node 1 dcgmi profile --pause"
       ],
       srun_options={
           "n": 4,
           "c": 8,
           "cpu-bind": "cores",
           "G": 4,
           "gpu-bind": "single:1"
       }
       srun_append="nsys profile --stats=true -t cuda --gpu-metrics-device=all",
       postrun_commands=[
           "srun --ntasks-per-node 1 dcgmi profile --resume",
       ]
   )

   @ct.electron(executor=executor)
   def my_custom_task(x, y):
       return x + y

Here the corresponding submit script contains the following commands:

.. code:: sh

   module load package/1.2.3
   srun --ntasks-per-node 1 dcgmi profile --pause

   srun -n 4 -c 8 --cpu-bind=cores -G 4 --gpu-bind=single:1 \
   nsys profile --stats=true -t cuda --gpu-metrics-device=all \
   python /scratch/user/experiment1/workflow_script.py

   srun --ntasks-per-node 1 dcgmi profile --resume


sshproxy
--------

Some users may need two-factor authentication (2FA) to connect to a cluster.  This plugin supports one form of 2FA using the `sshproxy <https://docs.nersc.gov/connect/mfa/#sshproxy>`_ service developed by NERSC. When this plugin is configured to support ``sshproxy``, the user's SSH key and certificate will be refreshed automatically by Covalent if either it does not exist or it is expired.  We assume that the user has already `configured 2FA <https://docs.nersc.gov/connect/mfa/#creating-and-installing-a-token>`_, used the ``sshproxy`` service on the command line without issue, and added the executable to their ``PATH``. Note that this plugin assumes the script is called ``sshproxy``, not ``sshproxy.sh``.  Further note that using ``sshproxy`` within Covalent is not required; a user can still run it manually and provide ``ssh_key_file`` and ``cert_file`` in the plugin constructor.

In order to enable ``sshproxy`` in this plugin, add the following block to your Covalent configuration while the server is stopped:

.. code:: bash

    [executors.slurm.sshproxy]
    hosts = [ "perlmutter-p1.nersc.gov" ]
    password = "<password>"
    secret = "<mfa_secret>"

For details on how to modify your Covalent configuration, refer to the documentation `here <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html?highlight=configuration>`_.

Then, reinstall this plugin using ``pip install covalent-slurm-plugin[sshproxy]`` in order to pull in the ``oathtool`` package which will generate one-time passwords.

The ``hosts`` parameter is a list of hostnames for which the ``sshproxy`` service will be used.  If the address provided in the plugin constructor is not present in this list, ``sshproxy`` will not be used.  The ``password`` is the user's password, not including the 6-digit OTP.  The ``secret`` is the 2FA secret provided when a user registers a new device on `Iris <https://iris.nersc.gov>`_.  Rather than scan the QR code into an authenticator app, inspect the Oath Seed URL for a string labeled ``secret=...``, typically consisting of numbers and capital letters.  Users can validate that correct OTP codes are being generated by using the command ``oathtool <secret>`` and using the 6-digit number returned in the "Test" option on the Iris 2FA page.  Note that these values are stored in plaintext in the Covalent configuration file.  If a user suspects credentials have been stolen or compromised, contact your systems administrator immediately to report the incident and request deactivation.

.. autoclass:: covalent.executor.SlurmExecutor
    :members:
    :inherited-members:
