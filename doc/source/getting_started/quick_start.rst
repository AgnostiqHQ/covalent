=================
Quick Start Guide
=================

To quickly install Covalent and run a short demo, follow the four steps below.

.. admonition:: Before you start

   Ensure you are using a compatible OS and Python version. See the :doc:`Compatibility <./compatibility>` page for supported Python versions and operating systems.


1. Use Pip to install the Covalent server and libraries locally.

  Type the following in a terminal window:

  .. code:: bash

      $ pip install covalent

2. Start the Covalent server.

  In the terminal window, type:

  .. code:: console

      $ covalent start
      Covalent server has started at http://localhost:48008

3. Run a workflow.

Open a Jupyter notebook or Python console and run the following Python code:

.. code:: python

    import covalent as ct

    # Construct tasks as "electrons".
    # Convert Python functions to electrons by
    # simply adding the electron decorator.
    @ct.electron
    def add(x, y):
        return x + y

    @ct.electron
    def multiply(x, y):
        return x*y

    @ct.electron
    def divide(x, y):
        return x/y

    # Construct the workflow as a "lattice"
    # using the electrons defined above.
    @ct.lattice
    def workflow(x, y):
        r1 = add(x, y)
        r2 = [multiply(r1, y) for _ in range(4)]
        r3 = [divide(x, value) for value in r2]
        return r3

    # Dispatch the workflow.
    dispatch_id = ct.dispatch(workflow)(1, 2)
    result = ct.get_result(dispatch_id, wait=True)
    print(result.result)

4. View the workflow progress.

  Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

  .. image:: ./../_static/qs_ui_queue.png
    :align: center

  Click on the dispatch ID to view the workflow graph:

  .. image:: ./../_static/qs_ui_graph.png
    :align: center


What to Do Next
###############

Read :doc:`Concepts <../concepts/concepts>` to gain a deeper understanding of how Covalent works.

See the :doc:`Tutorials <../tutorials/tutorials>` to see how to apply Covalent to real-world machine learning problems in a variety of subject domains.

See the :doc:`API Reference <../api/index>` for usage information on ``electron``, ``lattice``, and ready-to-use executors.

See :doc:`AWS Plugins <../api/executors/awsplugins>` to see how you can specify an executor to run this example on an AWS node using only two more lines of code.
