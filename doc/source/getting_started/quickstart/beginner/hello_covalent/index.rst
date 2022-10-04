======
Hello, Covalent!
======

Let's look at a simple example to get started with Covalent. Before starting, ensure you have installed Covalent, verified the installation, and started the Covalent server. Next, open a Jupyter notebook or Python console and create a simple workflow:


.. code:: python

   import covalent as ct

   # Construct tasks as "electrons"
   @ct.electron
   def join_words(a, b):
       return ", ".join([a, b])

   @ct.electron
   def excitement(a):
       return f"{a}!"

   # Construct a workflow of tasks
   @ct.lattice
   def simple_workflow(a, b):
       phrase = join_words(a, b)
       return excitement(phrase)

   # Dispatch the workflow
   dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")

Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

|

.. image:: hello_covalent_queue.png
   :align: center


Click on the dispatch ID to view the workflow graph:

|

.. image:: hello_covalent_graph.png
   :align: center


While the workflow is being processed by the dispatch server, you are free to terminate the Jupyter kernel or Python console process without losing access to the results. Make sure the Covalent server remains in the "running" state while you have running workflows.

When the workflow has completed, you can start a new session and query the results:

.. code:: python

   import covalent as ct

   dispatch_id = "8a7bfe54-d3c7-4ca1-861b-f55af6d5964a"
   result_string = ct.get_result(dispatch_id).result

When you are done using Covalent, stop the server:

.. code:: console

   $ covalent stop
   Covalent server has stopped.

Even if you forget to query or save your workflow results, Covalent saves them after each task's execution. The full results, including metadata, are stored on disk in the format shown below:

.. code:: text

    📂 my_project/
    ├─ 📙 my_experiment.ipynb
    ├─ 📂 results/
    │  ├─ 📂 8a7bfe54-d3c7-4ca1-861b-f55af6d5964a/
    │  │  ├─ 📄 result.pkl
    │  │  ├─ 🗒️ dispatch_script.py
    │  │  ├─ 🧾 result_info.yaml

Read more about how Covalent works on the Covalent :doc:`concepts <../concepts/concepts>` page.
