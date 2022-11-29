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