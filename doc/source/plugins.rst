.. include:: ../api/executors/

***************
🔗 Plugins
***************

Covalent offers various forms of plugins, first set of which are executor Plugins. These plugins are used to execute commands on the various kind of backends. Executors are responsible for taking a task and executing it in a certain place in a certain way. For example, the local executor invokes the task on the user's local computer. Users can define custom executors to make Covalent compatible with any remote backend system and covalent has a wide range of executor plugin libraries that connects to various resources from local Slurm cluster to cloud based AWS/GCP/Azure resources.

.. toctree::
   :maxdepth: 1
   :caption: Executor Plugins

   api/executors/dask
   api/executors/ssh
   api/executors/ec2.rst
   api/executors/slurm
   api/executors/awslambda.rst
   api/executors/awsbatch.rst
   api/executors/awsecs.rst
   api/executors/awsbraket.rst
