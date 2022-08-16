===============
Version Migration Guide
===============

Why migrate?
############

We always recommend using the latest version of covalent in order to get the latest improvements to our UI as well as potential speedups in workflow execution.

Migration Guide to 0.177.0
############

If you are currently using covalent version 0.110.2 you can upgrade to covalent version 0.177.0 or later as follows.

By running the following commands you can verify your covalent python as well as stop covalent and purge any config files present.

.. code:: bash

   $ pip show covalent | grep Version
   Version: 0.110.2
   $ covalent stop
   Covalent server has stopped.

You can install the new version of covalent by using pip.

.. code:: bash

   $ pip install covalent==0.177.0 --upgrade
   $ pip show covalent | grep Version
   Version: 0.177.0
   $ covalent db migrate
   INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
   INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
   INFO  [alembic.runtime.migration] Running upgrade  -> b60c5ecdf927, init
   INFO  [alembic.runtime.migration] Running upgrade b60c5ecdf927 -> 9b9d58f02985, v11
   Migrations are up to date.
   $ covalent start
   Covalent server has started at http://localhost:48008


You should then be able to use our data migration tool to migrate any workflows you may want to port over to the new version of covalent.

For example for a workflow with dispatch id :code:`e0ba03a2-fdc0-474e-9997-7fa8e82932c5`

.. code:: bash

   $ covalent migrate-legacy-result-object ./results/e0ba03a2-fdc0-474e-9997-7fa8e82932c5/result.pkl
   Processing result object for dispatch e0ba03a2-fdc0-474e-9997-7fa8e82932c5
   Processing node 0
   Processing node 1
   Processing node 2
   Processing node 3
   Processed transport graph
   Processed lattice

You should now be able to navigate to the UI (http://localhost:48008) and see your existing workflows.
