.. _gcpbatch_executor:

🔌 Google Batch Executor
""""""""""""""""""""""""

.. image:: Azure_Batch.png

Covalent Google Batch executor is an interface between Covalent and `Google Cloud Platform's Batch compute service <https://cloud.google.com/batch/docs/get-started>`_. This executor allows execution of Covalent tasks on Google Batch compute service.

This batch executor is well suited for tasks with high compute/memory requirements. The compute resources required can be very easily configured/specified in the executor's configuration. Google Batch scales really well thus allowing users to queue and execute multiple tasks concurrently on their resources efficiently. Google's Batch job scheduler manages the complexity of allocating the resources needed by the task and de-allocating them once the job has finished.


===============
1. Installation
===============

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

    pip install covalent-gpcbatch-plugin
