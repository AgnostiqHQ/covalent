==================
Running a Workflow
==================

With Covalent installed, you're ready to start the server and run workflows.

Starting the Server
###################

Start the Covalent server from the command line.

.. code:: console

   $ covalent start
   Covalent server has started at http://localhost:48008

Managing the Server
~~~~~~~~~~~~~~~~~~~

Use the Covalent CLI tool, ``covalent``, to manage the Covalent server. You can start and stop the server, view its status, and see the server logs.

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

Using the UI to View Workflows and Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

View the Covalent UI in your web browser at http://localhost:48008. This is where dispatched jobs will appear.


Running a Workflow
##################

Run this example to see Covalent in action.

Before starting, ensure that you have installed Covalent, verified the installation, and started the Covalent server.

Open a Jupyter notebook or Python console and create the following workflow:


.. code:: python

  import covalent as ct

      @ct.electron(
          executor=executor
      )
      def compute_pi(n):
          # Leibniz formula for π
          return 4 * sum(1.0/(2*i + 1)*(-1)**i for i in range(n))

      @ct.lattice
      def workflow(n):
          return compute_pi(n)


      dispatch_id = ct.dispatch(workflow)(100000000)
      result = ct.get_result(dispatch_id=dispatch_id, wait=True)
      print(result.result)

Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue. Click on the dispatch ID to view the workflow graph.

While the workflow is being processed by the dispatch server, you can terminate the Jupyter kernel or Python console process without losing access to the results. Make sure the Covalent server remains in the "running" state while you have running workflows.

When you are done using Covalent to run workflows, stop the server:

.. code:: console

   $ covalent stop
   Covalent server has stopped.
