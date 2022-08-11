.. _executors:

Executors
==========

.. image:: cova_archi.png
   :align: right
   :alt: cova_archi
   :height: 200px


Executors are responsible for taking a task and executing it in a certain place in a certain way. For example, the local executor invokes the task on the user's local computer. Users can define custom executors to make Covalent compatible with any remote backend system and covalent has a wide range of executor plugin libraries that connects to various resources from local Slurm cluster to cloud based AWS/GCP/Azure resources.

Plugins
**********
.. toctree::
   :maxdepth: 1

   local
   dask
   ssh
   slurm
   awsbraket

Base executor
*************

The way in which workflows and tasks interface with the hardware is through executor plugins, such as the local/dask executor packaged with core Covalent. While the Covalent team has a rigorous roadmap to provide interfaces to many devices, you may find that you want more flexibility or customization for a particular environment. Here, we recommend creating a custom executor plugin. `This repository <https://github.com/AgnostiqHQ/covalent-executor-template/>`_ serves as a template for creating such plugins. But one can also easily create a custom executor plugin by subclassing the following methods (for detailed instruction, please refer to How to create a custom executor plugin in how-to section of the documentation):


.. toctree::
   :maxdepth: 1

   basesync
   baseasync
