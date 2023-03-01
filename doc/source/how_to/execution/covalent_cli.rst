############################
Managing the Covalent Server
############################

Covalent provides a command line interface (CLI) to start, stop, and check the status of the server. Covalent also provides a browser-based GUI to view and manage workflow dispatches and results.

Prerequisites
-------------

Before using any of the Covalent server tools, you must:

1. :doc:`Install<../../getting_started/quick_start/index>` the Covalent package.
2. Activate the Python environment where the Covalent package has been installed.

Procedures
----------

Starting the Server
~~~~~~~~~~~~~~~~~~~

In order to dispatch lattice workflows for execution, you must start the Covalent server.

To start the server, use the following command:

.. code-block:: sh

    $ covalent start
    Covalent server has started at http://localhost:48008

.. note:: By default, the server port is set to :code:`48008`.

Using the GUI
~~~~~~~~~~~~~

Use the Covalent GUI to view and manage workflow dispatches and results.

Navigate to http://localhost:48008 to view the Covalent GUI.

Checking the Server Status
~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the server status using the following command:

.. code-block:: sh

    $ covalent status
    Covalent server is running at http://localhost:48008.

Stopping the Server
~~~~~~~~~~~~~~~~~~~

Use the following command to stop the server:

.. code-block:: sh

    $ covalent stop
    Covalent server has stopped.

Restarting the Server
~~~~~~~~~~~~~~~~~~~~~

To stop and restart the server (for example, to pick up a changed parameter in the configuration):

.. code-block:: sh

    $ covalent restart
    Covalent server has stopped.
    Covalent server has started at http://localhost:48008

Using a Custom Port
~~~~~~~~~~~~~~~~~~~

You can force the server to use a port other than the default if necessary. To specify a custom port, use the `--port` flag:

.. code-block:: sh

    $ covalent start --port 5001
    Covalent server has started at http://localhost:5001

The default port value can also be changed in the global config file as discussed in :doc:`Configuration Customization<../config/customization>` in the How-To Guide.

Resetting the Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

At some point you might need to reset the server configuration to the shipped defaults.

.. warning::

    Resetting the configuration deletes all directories referenced in the config file, including log and cache directories, with the exception of the results directory.


Reset the configuration using the :code:`purge` subcommand:

.. code-block:: sh

    $ covalent purge
    Covalent server files have been purged.
