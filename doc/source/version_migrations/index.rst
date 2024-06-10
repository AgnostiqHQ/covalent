=======================
Version Migration Guide
=======================

Why Migrate?
############

We recommend always using the latest version of Covalent in order to get the latest improvements to the UI, use the latest features, and to take advantage of improvements in workflow execution speed.

Migrating to the Current Version
################################

If you are using Covalent v0.110.2 or later you can upgrade to Covalent v0.177.0 or later as follows:

1. Identify the currently installed version.

  .. code:: bash

     $ pip show covalent | grep Version
     Version: 0.110.2

2. Stop the server.

  .. code:: bash

     $ covalent stop
     Covalent server has stopped.

3. Install the new version of Covalent using Pip.

  .. code:: bash

     $ pip install covalent==0.202.0 --upgrade
     $ pip show covalent | grep Version
     Version: 0.202.0

4. Migrate the database.

  .. code:: bash

     $ covalent db migrate
     INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
     INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
     INFO  [alembic.runtime.migration] Running upgrade  -> b60c5ecdf927, init
     INFO  [alembic.runtime.migration] Running upgrade b60c5ecdf927 -> 9b9d58f02985, v11
     Migrations are up to date.

5. Start the server.

  .. code:: bash

     $ covalent start
     Covalent server has started at http://localhost:48008

6. Navigate to the UI (http://localhost:48008) to view your workflows.
