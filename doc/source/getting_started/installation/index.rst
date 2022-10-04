=====
Installation Guide
=====

Upgrading Covalent
~~~~~~~~~~~~~~~~~~

If you are upgrading Covalent from the previous stable release, please refer to the :doc:`migration guide <./../version_migrations/index>` if you wish to preserve your data and/or avoid any issues that may arise when upgrading.

Installation Methods
~~~~~~~~~~~~~~~~~~~~

Pip Install
-----------

The easiest way to install Covalent is using the PyPI package manager:

.. code:: bash

   pip install covalent

.. note::

   If you have used Covalent previously, make sure to uninstall the Covalent Dask plugin by running :code:`pip uninstall covalent-dask-plugin`. That plugin has been folded into Covalent and will no longer be maintained separately.


Conda Install
-------------

Users can also install Covalent as a package in a Conda environment:

.. code:: bash

   conda install -c agnostiq covalent

.. note::

   Installation via Conda is currently only supported for Linux. Sometimes Conda can have trouble resolving packages. Use the flag :code:`--override-channels` to speed things up.

Install From Source
--------------------

Covalent can also be downloaded and installed from source:

.. code:: bash

   git clone git@github.com:AgnostiqHQ/covalent.git
   cd covalent

   # Build dashboard
   python setup.py webapp

   # Install using pip (-e for developer mode), or...
   pip install -e .

   # Build and install using Conda (10-15 mins)
   conda build .
   conda install -c local covalent

The documentation can also easily be built locally:

.. code:: bash

   python setup.py docs


Validate the Installation
~~~~~~~~~~~~~~~~~~~~~~~~~

You can validate Covalent has been properly installed if the following returns without error:

.. code:: bash

   python -c "import covalent"

Start the Server
#################

Use the Covalent CLI tool to manage the Covalent server. The following commands will help you get started.

.. code:: console

   $ covalent --help
   Usage: covalent [OPTIONS] COMMAND [ARGS]...

   Covalent CLI tool used to manage the servers.

   Options:
   -v, --version  Display version information.
   --help         Show this message and exit.

   Commands:
   logs     Show Covalent server logs.
   purge    Shutdown server and delete the cache and config settings.
   restart  Restart the server.
   start    Start the Covalent server.
   status   Query the status of the Covalent server.
   stop     Stop the Covalent server.

Start the Covalent server:

.. code:: console

   $ covalent start
   Covalent server has started at http://localhost:48008

Optionally, confirm the server is running:

.. code:: console

   $ covalent status
   Covalent server is running at http://localhost:48008.

Now, navigate to the Covalent UI by entering the address into your web browser.  This is where dispatched jobs will appear.
