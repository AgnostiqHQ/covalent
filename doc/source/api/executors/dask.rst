.. _dask_executor:

Dask Executor
"""""""""""""""""""""""""""

Executing tasks (electrons) in a Dask cluster. This is the default executor when covalent is started without the :code:`--no-cluster` flag.

.. code:: python

    from dask.distributed import LocalCluster

    cluster = LocalCluster()
    print(cluster.scheduler_address)


The address will look like :code:`tcp://127.0.0.1:55564` when running locally. Note that the Dask cluster does not persist when the process terminates.

This cluster can be used with Covalent by providing the scheduler address:

.. code:: python

    import covalent as ct

    dask_executor = ct.executor.DaskExecutor(
                        scheduler_address="tcp://127.0.0.1:55564"
                    )

    @ct.electron(executor=dask_executor)
    def my_custom_task(x, y):
        return x + y

    ...


.. autoclass:: covalent.executor.executor_plugins.dask.DaskExecutor
    :members:
    :inherited-members:
