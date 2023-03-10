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


===========================================
2. Usage Example
===========================================

Here we present an example on how a user can use the GCP Batch executor plugin in their Covalent workflows. In this example we train a simple SVM (support vector machine) model using the Google Batch executor. This executor is quite minimal in terms of the required cloud resoures that need to be provisioned prior to first use. The Google Batch executor needs the following cloud resources pre-configured 

* A Google storage bucket
* Cloud artifact registry for Docker images
* A service account with the following permissions
  * 

This is an example of how a workflow can be adapted to utilize the AWS Batch Executor. Here we train a simple Support Vector Machine (SVM) model and use an existing AWS Batch Compute environment to run the :code:`train_svm` electron as a batch job. We also note we require :doc:`DepsPip <../../concepts/concepts>` to install the dependencies when creating the batch job.

