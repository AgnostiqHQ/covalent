###################################
Remedying Database Migration Errors
###################################

When upgrading Covalent versions from 0.177.0 to a newer version, you may need to run database migrations.

.. warning:: Ensure that you back up your database before attempting to alter it's data as follows :code:`cp ~/.local/share/covalent/dispatcher_db.sqlite /some/safe/location/dispatcher_db.sqlite` it may be worth opening an issue in the covalent repo to get additional guidance from maintainers about the specific migration issue in question.

In a small number of cases, migrations can fail to run because existing data violates SQL database constraints, or for other reasons specific to the type of schema update.

For example, the following migration fails due to existing data in the database.

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

In this above example, :code:`electron_id` is now prohibited from having NULL values, but there are NULL values in the existing database.

To remedy the situation, data that violates this constraint is removed manually from the database. By default, the Covalent database is an SQLlite database has this file path: :code:`~/.local/share/covalent/dispatcher_db.sqlite`.

Making these changes requires advanced knowledge of Covalent. It is not recommended unless you are fully acquainted with how Covalent works, since it may cause unexpected behavior.

Lastly, if you are unable to solve the issue in this manner, you may need to delete the database and re-run the migrations as follows.

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

At this point you may start Covalent as before with :code:`covalent start`
