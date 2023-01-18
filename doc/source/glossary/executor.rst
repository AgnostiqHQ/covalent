########
Executor
########

In Covalent, an interface to a computational resource. The compute resource is said to *back*, or be the "backend" for, the executor. The backend can be local, remote, or cloud-based. A single executor is backed by exactly one resource (though that resource could be a :doc:`cluster<cluster>`).

A :doc:`workflow<workflow>` can have access to any number of executors, backed by any number of different resources of any number of types. Each :doc:`task<task>` within the workflow is assigned an executor, explicitly or by default.

Covalent comes with a default executor backed by a local :doc:`Dask<dask>` cluster.
