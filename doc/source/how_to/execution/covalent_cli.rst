============
How to manage the Covalent server
============

In order to dispatch lattice workflows for execution, the user needs to start the Covalent server. The pre-requisite is the installation of the Covalent package. Then, the python environment where the Covalent package has been installed needs to be activated. Covalent provides a Command Line Interface (CLI) to start, stop or check the status of the server in the shell. In order to start the server, the following shell command can be used.

.. code-block:: sh

    $ covalent start
    Covalent server has started at http://localhost:48008

.. note:: By default, the server port is set to `48008`. Users should navigate to http://localhost:48008 to view the browser-based UI.

The user can check the server status using the command below.

.. code-block:: sh

    $ covalent status
    Covalent server is running at http://localhost:48008.

In order to stop the server, use the shell command below.

.. code-block:: sh

    $ covalent stop
    Covalent server has stopped.

Covalent also lets the user stop and restart the server via:

.. code-block:: sh

    $ covalent restart
    Covalent server has stopped.
    Covalent server has started at http://localhost:48008

Custom ports can be specified using the `--port` flag.

.. code-block:: sh

    $ covalent start --port 5001
    Covalent server has started at http://localhost:5001

It is important to note that the default port value can also be specified in the global config file as discussed in the :doc:`configuration customization<../config/customization>` how-to guide.

Lastly, the config file can be reset using the following command:

.. code-block:: sh

    $ covalent purge
    Covalent server files have been purged.

This is useful when the user wishes to reset the default port value etc.

.. warning::

    This will also delete all directories referenced in the config file (logs, caches) with the exception of the results directory.
