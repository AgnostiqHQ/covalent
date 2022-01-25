============
How to manage the Covalent server
============

In order to dispatch lattice workflows for execution, the user needs to start the Covalent server. The pre-requisite is the installation of the Covalent package. Then, the python environment where the Covalent package has been installed needs to be activated. Covalent provides a Command Line Interface (CLI) to start, stop or check the status of the server in the shell. In order to start the server, the following shell command can be used.

.. code-block:: sh

    $ covalent start
    Covalent dispatcher server has started at http://0.0.0.0:48008
    Covalent UI server has started at http://0.0.0.0:47007

.. note:: By default, the dispatcher server port is set to `48008` and the UI server port is set to `47007`. Users should navigate to http://0.0.0.0:47007 to view the browser-based UI.

The user can check the server status using the command below.

.. code-block:: sh

    $ covalent status
    Covalent dispatcher server is running at http://0.0.0.0:48008.
    Covalent UI server is running at http://0.0.0.0:47007.

In order to stop the server, use the shell command below.

.. code-block:: sh

    $ covalent stop
    Covalent dispatcher server has stopped.
    Covalent UI server has stopped.

Covalent also lets the user stop and restart the server via:

.. code-block:: sh

    $ covalent restart
    Covalent dispatcher server has stopped.
    Covalent dispatcher server has started at http://0.0.0.0:48008
    Covalent UI server has stopped.
    Covalent UI server has started at http://0.0.0.0:47007

Custom ports can be specified using the `--port` flag.

.. code-block:: sh

    $ covalent start --port 5001
    Covalent dispatcher server has started at http://0.0.0.0:5001
    Covalent UI server has started at http://0.0.0.0:47007

It is important to note that the default port value can also be specified in the global config file as discussed in the :doc:`configuration customization<../config/customization>` how-to guide.

Lastly, the config file can be reset using the following command:

.. code-block:: sh

    $ covalent purge
    Covalent server files have been purged.

This is useful when the user wishes to reset the default port value etc.

.. warning::

    This will also delete all directories referenced in the config file (logs, caches) with the exception of the results directory.
