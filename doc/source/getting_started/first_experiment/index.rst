===============
First experiment
===============

This page describes how to get started with Covalent. Follow the procedures on this page to:

    1. Install Covalent;
    2. Start the Covalent server;
    3. Run a workflow using Covalent; and
    4. View the workflow using the browser-based interface (GUI).

Installing Covalent
###################

.. admonition:: Before you start

  Ensure you are using a compatible OS and Python version. See the :doc:`Compatibility <./compatibility>` page for supported Python versions and operating systems.

You can install Covalent using Pip, the Python package manager, or you can download the Covalent source repository from GitHub and build Covalent yourself. Unless you are contributing to Covalent or have some other compelling reason to build from source, we strongly recommend using Pip. To build from source, see :doc:`Building and Installing Covalent from Source <build_from_source>`.

.. important:: If you are upgrading Covalent from a previous stable release, refer to the :doc:`migration guide <./../../version_migrations/index>` to preserve your data and avoid upgrade problems.


Installing with Pip
~~~~~~~~~~~~~~~~~~~

To install Covalent using Pip, type the following on the command line:

.. code:: bash

    $ pip install covalent


Validating the Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optionally, validate the installation. Covalent has been properly installed if the following returns without error:

.. code:: bash

    $ python -c "import covalent"


Starting the Server
###################

Start the Covalent server from the command line:

.. code:: console

    $ covalent start
    Covalent server has started at http://localhost:48008

At any time, you can verify that the server is running by typing:

.. code:: console

    $ covalent status
    Covalent server is running at http://localhost:48008.


Stopping the Server
~~~~~~~~~~~~~~~~~~~

When you are done using Covalent to run workflows, stop the server.

.. warning::

    Do not stop the server while you have running workflows. Stopping the server will kill the workflows.

To stop the Covalent server:

.. code:: console

    $ covalent stop
    Covalent server has stopped.

Managing the Server
~~~~~~~~~~~~~~~~~~~

Use the Covalent CLI tool, ``covalent``, to manage the Covalent server. You can start and stop the server, view its status, and view the server logs.

View available subcommands with the --help option:

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

You can also view help for any subcommand. For example:

.. code:: console

    $ covalent stop --help
    Usage: covalent stop [OPTIONS]

        Stop the Covalent server.

        Options:
        --help  Show this message and exit.


Running a Workflow
##################

Follow the steps below to run an example workflow.

.. admonition:: Before you start

    Ensure that you have installed Covalent and started the Covalent server.

1. Open a Jupyter notebook or Python console.

2. In the notebook, create a workflow by typing (or pasting) the following Python code:

.. code:: python

    import covalent as ct

    executor = ct.executor.LocalExecutor()

    @ct.electron(
        executor=executor
    )
    def compute_pi(n):
        # Leibniz formula for π
        return 4 * sum(1.0/(2*i + 1)*(-1)**i for i in range(n))

        @ct.lattice
        def workflow(n):
        return compute_pi(n)

        dispatch_id = ct.dispatch(workflow)(1000)
        result = ct.get_result(dispatch_id=dispatch_id, wait=True)
        print(result.result)


Viewing the Workflow
####################

Do the following to view your workflow in the GUI.

1. Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

.. image:: ./../../_static/ui_list_pi_wf.png
    :align: center

.. note:: With n = 1000, the workflow finishes quickly (less than one second, as shown above.)

2. Set n to a large value to see the workflow still running in the UI.

    Change the number of iterations in the example code:

.. code:: python

    dispatch_id = ct.dispatch(workflow)(10000000)

.. image:: ./../../_static/ui_list_pi_wf_running.png
    :align: center

3. Click on the dispatch ID to view the workflow graph:

.. image:: ./../../_static/ui_detail_pi_wf.png
    :align: center

While the workflow is being processed by the dispatch server, you can terminate the Jupyter kernel or Python console process without losing access to the results.

.. warning:: Do not stop the Covalent server while you have running workflows. Stopping the server will kill the workflows.


What to Do Next
###############

Read :doc:`Concepts <../../concepts/concepts>` gain a deeper understanding of how Covalent works.

See the :doc:`Tutorials <../../tutorials/tutorials>` to see how to apply Covalent to real-world machine learning problems in a variety of subject domains.

See the :doc:`API Reference <../../api/index>` for usage information on ``electron``, ``lattice``, and ready-to-use executors.

See :doc:`AWS Plugins <../../api/executors/awsplugins>` to see how you can specify an executor to run this example on an AWS node using only two more lines of code.
