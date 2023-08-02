.. include:: ../api/executors/

******************************
:octicon:`plug;1em;`  Plugins
******************************

Covalent offers various plugins, starting with executor plugins. Executors are used to run tasks on the various kinds of backends. Executors decouple a task from hardware details by executing the task in a certain place in a certain way. For example, the *local* executor invokes the task on the user's local computer. You can define custom executors to make Covalent compatible with any remote backend system. Covalent has a wide range of executor plugin libraries that connect to a variety of resources, from local Slurm clusters to cloud-based AWS, GCP, and Azure compute nodes and more.

.. toctree::
   :maxdepth: 1
   :caption: Executor Plugins

   api/executors/dask
   api/executors/ssh
   api/executors/slurm
   api/executors/awsplugins
   api/executors/awsec2.rst
   api/executors/awslambda.rst
   api/executors/awsbatch.rst
   api/executors/awsecs.rst
   api/executors/awsbraket.rst
   api/executors/azurebatch.rst
   api/executors/gcpbatch.rst

.. toctree::
   :maxdepth: 1
   :caption: Quantum Executor Plugins

   api/executors/qiskit.rst
   api/executors/ibmq.rst
   api/executors/braketqubit.rst
   api/executors/localbraketqubit.rst
