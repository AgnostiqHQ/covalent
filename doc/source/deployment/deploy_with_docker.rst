Deployment with Docker
######################

To run Covalent as a Docker container using public images, do the following.

.. card:: 1. Get the latest Docker image for Covalent with:

    .. code:: bash

        docker pull public.ecr.aws/covalent/covalent:latest

    .. note::  To get the current stable image of Covalent, use ``stable`` instead of ``latest``.

.. card:: 2. Start Covalent:

    .. code:: bash

        docker container run -d --name covalent -p 48008:48008 public.ecr.aws/covalent/covalent:latest

    This starts the container in detached mode and forwards port ``48008`` to the host.

.. card:: 3. To view the Covalent GUI, go to `http://localhost:48008 <http://localhost:48008>`_.

.. card:: 4. Configure Covalent inside the container with environment variables.

The following table lists the environment variables available to customize Covalent's execution environment at startup:

.. list-table:: Covalent configuration environment variables
   :widths: 20 80
   :header-rows: 1

   * - Environment Variable
     - Description
   * - COVALENT_ROOT
     - Root directory for the ``covalent`` process
   * - COVALENT_CONFIG_DIR
     - Directory that ``covalent`` searches for its configuration file, ``covalent.conf``
   * - COVALENT_PLUGINS_DIR
     - Path where ``covalent`` looks to load any installed executor plugins
   * - COVALENT_DATABASE
     - Path to ``covalent``'s backend SQLite3 database
   * - COVALENT_LOGDIR
     - Path to ``covalent``'s log file
   * - COVALENT_CACHE_DIR
     - Directory used by ``covalent`` to store temporary objects during runtime
   * - COVALENT_DATA_DIR
     - Path to ``covalent``'s database directory
   * - COVALENT_RESULTS_DIR
     - Directory in which to store intermediate result objects
   * - COVALENT_SVC_PORT
     - TCP port on which ``covalent`` runs
   * - COVALENT_SERVER_IFACE_ANY
     - Boolean flag that causes ``covalent`` to listen on all network interfaces on the host
   * - COVALENT_NUM_WORKERS
     - Number of Dask workers in Covalent's default cluster
   * - COVALENT_MEM_PER_WORKER
     - Memory limit for each Dask worker
   * - COVALENT_THREADS_PER_WORKER
     - Number of threads with which to start each worker


.. card:: 5. For example, to start Covalent with two workers on port 8000:

    .. code:: bash

       docker container run --name covalent -p 8000:8000 -e COVALENT_NUM_WORKERS=2 -e COVALENT_SVC_PORT=8000 public.ecr.aws/covalent/covalent:latest
