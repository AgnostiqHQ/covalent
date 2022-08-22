===============
Database Migration Errors
===============

How to approach failed database schema migrations
############

When upgrading Covalent versions from 0.177.0 to a newer version we may require running database migrations, however in some edge cases migrations may fail to run as a result of having existing data that violates SQL database constraints and/or other reasons specific to the type of schema updates that may occur.

For example the following migration causes an issue due to existing data in the database.

.. code:: bash

   $ covalent db migrate
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade 9b9d58f02985 -> 9f1271ef662a, v11+ updates
    (sqlite3.IntegrityError) NOT NULL constraint failed: _alembic_tmp_lattices.electron_id
    [SQL: INSERT INTO _alembic_tmp_lattices (id, dispatch_id, electron_id, name, status, electron_num, completed_electron_num, storage_type, storage_path, function_filename, function_string_filename, error_filename, inputs_filename, results_filename, transport_graph_filename, is_active, created_at, updated_at, started_at, completed_at, executor, executor_data_filename, workflow_executor, workflow_executor_data_filename, named_args_filename, named_kwargs_filename) SELECT lattices.id, lattices.dispatch_id, lattices.electron_id, lattices.name, lattices.status, lattices.electron_num, lattices.completed_electron_num, lattices.storage_type, lattices.storage_path, lattices.function_filename, lattices.function_string_filename, lattices.error_filename, lattices.inputs_filename, lattices.results_filename, lattices.transport_graph_filename, lattices.is_active, lattices.created_at, lattices.updated_at, lattices.started_at, lattices.completed_at, lattices.executor, lattices.executor_data_filename, lattices.workflow_executor, lattices.workflow_executor_data_filename, lattices.named_args_filename, lattices.named_kwargs_filename
    FROM lattices]
    (Background on this error at: https://sqlalche.me/e/14/gkpj)
    There was an issue running migrations.
    Please read https://covalent.readthedocs.io/en/latest/how_to/db/migration_error.html for more information.

.. warning:: Ensure that you back up your database before attempting to alter it's data as follows :code:`cp ~/.local/share/covalent/dispatcher_db.sqlite /some/safe/location/dispatcher_db.sqlite` it may be worth opening an issue in the covalent repo to get additional guidance from maintainers about the specific migration issue in question.

There may be table alterations that fail as a result of some existing data in the database violating some SQL constraint. In the above example that shows the migration error electron_id is now intended to not have NULL values however NULL values may be present in our database.
In order to avoid the migration issue we must remove any data that violates this constraint manually in the SQLlite database which resides in :code:`~/.local/share/covalent/dispatcher_db.sqlite`.
Doing so requires advanced knowledge of covalent as is not recommended unless you are fully aquainted with how covalent works as it may cause unexpected behavior.

Lastly, if unable to solve the issue in this manner you may need to delete the database and re-run the migrations as follows.

.. warning:: This will cause all of your workflow data to be deleted unless a backup of the database was created.


.. code:: bash

   $ covalent stop
    Covalent server has stopped.
   $ rm ~/.local/share/covalent/dispatcher_db.sqlite
   $ covalent db migrate
    INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
    INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
    INFO  [alembic.runtime.migration] Running upgrade  -> b60c5ecdf927, init
    INFO  [alembic.runtime.migration] Running upgrade b60c5ecdf927 -> 9b9d58f02985, v11
    INFO  [alembic.runtime.migration] Running upgrade 9b9d58f02985 -> 9f1271ef662a, v11+ updates
    Migrations are up to date.

At which point you may start covalent as before with :code:`covalent start`
