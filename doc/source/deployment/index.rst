*************************
Covalent Deployment Guide
*************************

Covalent supports both local and remote installations to suit different uses cases and compute requirements. For quick prototyping and testing running ``Covalent`` locally
might be sufficient but for dispatching large compute intensive workflows which may require lots of CPU cores and memory, deploying ``Covalent`` as a **remote** server (cloud/on-prem) would be a better alternative. This way
users can still develop their workflows locally and dispatch them to the remote Covalent server for execution.


Deployment with Docker
#######################

Apart from installing ``Covalent`` locally within a Python virtual environment, users can also run Covalent as a docker container using the public images. The latest docker image for ``Covalent`` can be obtained as

.. code:: bash

    docker pull public.ecr.aws/covalent/covalent:latest


.. note::

    To obtain the stable image, the ``stable`` tag can be used instead of ``latest``

Covalent can then be started by running the container as follows

.. code:: bash

    docker container run -d --name covalent -p 48008:48008 public.ecr.aws/covalent/covalent:latest

This will start the container in detached mode and map port ``48008`` back out to host. To view the UI, users can then go to `http://localhost:48008 <http://localhost:48008>`_. Users can still configure Covalent that's running inside the container via environment variables.
The following table lists out all the supported environment variables that users can specify to customize Covalent's execution environment at start up.

.. list-table:: Covalent configuration environment variables
   :widths: 20 80
   :header-rows: 1

   * - Environment Variable
     - Description
   * - COVALENT_ROOT
     - Root directory for the ``covalent`` process
   * - COVALENT_CONFIG
     - Directory that ``covalent`` will search for its configuration file, ``covalent.conf``
   * - COVALENT_PLUGINS_DIR
     - Path where ``covalent`` will look to load any executor plugins installed
   * - COVALENT_DATABASE
     - Path to ``covalent``'s backend SQLite3 database
   * - COVALENT_LOGDIR
     - Path to ``covalent``'s log file
   * - COVALENT_CACHE_DIR
     - Directory to be used by ``covalent`` for storing temporary objects during runtime
   * - COVALENT_DATA_DIR
     - Path to ``covalent``'s database directory
   * - COVALENT_SVC_PORT
     - TCP port on which ``covalent`` will start running
   * - COVALENT_SERVER_IFACE_ANY
     - Boolean value to allow ``covalent`` to listen on all network interfaces on the host
   * - COVALENT_NUM_WORKERS
     - Number of Dask workers to start as part of Covalent's default cluster
   * - COVALENT_MEM_PER_WORKER
     - Memory limit for each dask worker
   * - COVALENT_THREADS_PER_WORKER
     - Number of threads to start each worker with


As an example users can start Covalent with 2 workers on port 8000 as follows

.. code:: bash

   docker container run --name covalent -p 8000:8000 -e COVALENT_NUM_WORKERS=2 -e COVALENT_SVC_PORT=8000 public.ecr.aws/covalent/covalent:latest


==============================
On-prem deployment
==============================

The ``Covalent`` server can be installed and deployed on on-prem servers or virtual machines quite easily in order to centralize the deployment. This would enable users to host their Covalent servers on on-prem machines they may have access to or run them inside virtual machines. If the remote machines have `Docker <https://www.docker.com/>`_ support enabled then the deployment is trivally simple and amounts to simply pulling and running the Covalent container from our public registries. The deployment can be customized by following the steps outlined in :ref:`Deployment with Docker <Deployment with Docker>` section.



====================
Deployment on AWS
====================

Users can deploy Covalent in their own AWS accounts with any ``x86`` based EC2 instance of their choice. This can allow users to vertically scale up their workloads as they can choose the compute instance type that is optimal for their use case. There are several ways users can go about this as Covalent is already provided as a portable docker container. Users can deploy an EC2 virtual machine that is capable of running docker containers and simply follow the steps listed in :ref:`Deployment with Docker <Deployment with Docker>`
