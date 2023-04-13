############
Dask Cluster
############

Use the Dask Cluster Settings page to view preferences for the Dask cluster that backs the Covalent default executor. The Dask Cluster settings are not editable in the Covalent GUI, but can be configured as described in the `Dask documentation <https://docs.dask.org/en/stable/configuration.html>`_. In most cases there is no need to adjust the Dask configuration used with Covalent.

.. note:: If `No Cluster` is set to `True` in the :doc:`api` Settings page, then the Covalent server does not start the Dask cluster and instead uses the local executor by default.

.. image:: ../images/dask.png
  :align: center

Cache Directory
    The directory path that Dask uses for cacheing.
Log Directory
    The directory path of the Dask cluster logs.
Mem Per Worker
    The memory allocated per worker process. For larger workloads the default memory per worker for a local Dask cluster might be too small. See the `Dask worker memory documentation <https://distributed.dask.org/en/stable/worker-memory.html>`_ for information about setting worker memory. (This is an exception to the rule that the default Dask settings are adequate for most cases.)
Threads Per Worker
    The number of threads allocated to each worker node in the Dask cluster.
Num Workers
    The number of workers in the Dask cluster.
Scheduler Address
    The IP address and port for the Dask scheduler.
Dashboard Link
    The URL of the Dask dashboard.
Process Info
    The name and parent process of the Dask cluster.
PID
    The main process ID of the Dask cluster. This is the parent of the Dask worker processes.
Admin Host
    The IP address of the Dask admin UI. For the default Dask cluster, this is the local host.
Admin Port
    The port of the Dask admin UI.
