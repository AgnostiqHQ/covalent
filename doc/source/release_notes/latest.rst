******************************
Release Version |release|
******************************

The latest release of Covalent is now out and available for every great sole out there to use! It comes with huge improvements and changes in how Covalent is designed from being even more modular to handling large-scale tasks.



Covalent is even more modular
*******************************

**Covalent Microservices:** Covalent dispatcher was the central hub for all covalent tasks to be sent to for queued and executed on various hardware. With the current release, the most significant change comes from splitting this monolithic central hub into six different servers

.. image:: ./../_static/Covalent_Local_Microservices.png
   :width: 500
   :align: center

(Brief 2-3 lines for each entity here and add links to the APIs)

- Data
- Queuer
- Dispatcher
- Runner
- Results
- NATS Message Queue

Each of them has its own responsibility and works purely via APIs. Thus, in theory, one can host any of these servers on any machine they want. More importantly, Covalent would execute electrons on the device that the dispatcher is running when used with :code:`LocalExecuter`. But with the new architecture, the Runner service explicitly executes covalent's LocalExecution, which can be hosted in any machine, even high compute cloud machines!


Dask dependency removed
**************************

Previously, queuing various tasks and async execution was offloaded to `dask`. Although `dask` is really good at what it does, we moved away from it for various reasons, a few important ones being :

- **Dependency cut-down** - We wanted to have the most minimal dependency to get covalent up and running. We are working on reducing the dependency even further for future releases
- **Control-ability** - Being a tool to interface with advanced high-performance hardware, we wanted to have complete control over allocating resources, even in the local case.
- **Scalability** - Although Dask is very scalable for executing independent calculations, Covalent natively deals with not just single calculations but at the workflow level. We found dask to not scale and inefficient to allocate resources when running multiple experiments alongside
- **Modularity** - When creating resources with dask, one is often required to create an instance of :code:`Cluster`, which in theory is monolithic. To separate the heavy execution component and other objects like data transfer, queue etc., we wanted to break down Dask's responsibilities and create our own service for each individual piece that can be run on separate machines.

As a result, we now have better control over resource allocation, and scalable workflows.

Going beyond python
********************

**New language support:** Being true to our goal of democratizing advanced hardware, we understand that users might have native codes/scripts written in languages other than python that must be maintained/sent off to be computed. With this in mind, we extend the notion of :code:`electrons` to :code:`leptons`, a flavor of particle that is more general and can accept tasks from various languages. We currently have extended support for C/C++ and bash with :code:`julia` coming soon. :code:`Leptons` is meant as an easy addition to translating your existing non-pythonic tasks into Covalent workflow. Thereby covalent does not only let you **mix advanced hardware** in your experiments but also **intertwine programming languages!**.

.. code-block:: python

    task = ct.Lepton(language="C",
                     library_name="libtest.so",
                     function_name="test_entry",
                     argtypes=[ (c_int32, ct.Lepton.INPUT),
                                (POINTER(c_int32), ct.Lepton.INPUT_OUTPUT),
                                (POINTER(c_int32), ct.Lepton.OUTPUT)]
                    )

.. Note:: Leptons are meant to translate existing scripts from other languages easily into covalent workflows. When it comes to language support, we are working on two main fronts

    1. to provide native support for scripting languages like Julia, R and
    2. To provide functional access via python to languages like Bash where one can directly run terminal commands from python without needing to write a bash script.

New Executers
*************

As a fundamental principle of Covalent, we want things to be as modular as possible. This made us design executers - modular blocks of plugins that dictates and controls the choice of hardware resource your task is being run on. Being an open-source-focused team, we made it extremely easy for users to construct custom executers based on the template we have released. Using the same, we are releasing two new executers - :code:`SSHExecuter`, :code:`SLURMExecuter`.

- :code:`SSHExecuter` - Have you ever wondered if you can do a join hybrid experiment between a RasberryPi and Quantum computer? After a quick :code:`pip install covalent-ssh-plugin`, one gets the ability to interface Covalent with any machines accessible via SSH. This plugin can distribute tasks to one or more compute backends that are not controlled by a cluster management system, such as computers on a LAN, or even a collection of small-form-factor Linux-based devices such as Raspberry Pis, NVIDIA Jetsons, or Xeon Phi co-processors.
It is as simple as adding

.. code-block:: python

    executor = ct.executor.SSHExecutor(
                                        username="user",
                                        hostname="host2.hostname.org",
                                        remote_dir="/tmp/covalent",
                                        ssh_key_file="/home/user/.ssh/host2/id_rsa",)

    @ct.electron(executor=executor)
    def my_custom_task(x, y):
        return x + y


- :code:`SLURMExecuter` - One of the most used Open Source High-performance cluster job management systems - SLURM, is supported by covalent now! This executor plugin interfaces Covalent with HPC systems managed by `Slurm <https://slurm.schedmd.com/documentation.html>`_. For workflows to be deployable, users must have SSH access to the Slurm login node, writable storage space on the remote filesystem, and permissions to submit jobs to Slurm.

.. code-block:: python

    executor = ct.executor.SlurmExecutor(remote_workdir="/scratch/user/experiment1",
                                        conda_env="covalent",
                                        options={"partition": "compute","cpus-per-task": 8})

    @ct.electron(executor=executor)
    def my_custom_task(x, y):
        return x + y


Covalent theme/UI gets a makeover
***************************************

.. image:: ./../_static/Covalent_banner.svg
   :width: 500
   :align: center

To go along with these massive new backend changes and be inclusive of hardware beyond quantum, we have reworked Covalent colors and logos to reflect the truly diverse nature of the problems we are solving. Previously, a logo meant to indicate the connections made with "C" is now a logo of seemingly different shapes to demonstrate the variety of hardware/software/resource paradigms working in unison to create beautiful results. What used to be futuristic with neon colors has now transitioned to a more pastel feel to indicate the immediate need for such a tool. Hope you all enjoy it as much as we do!
