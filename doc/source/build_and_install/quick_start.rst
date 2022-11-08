=================
Quick Start Guide
=================

To quickly install Covalent and run a short demo, follow the four steps below.

.. admonition:: Before you start

  Ensure you are using a compatible OS and Python version. See the :doc:`Compatibility <./compatibility>` page for supported Python versions and operating systems.


Step 1: Install Covalent
########################

  Use Pip to install the Covalent server and libraries locally:

.. code:: bash

   pip install covalent


Step 2: Start the Server
########################

Start the Covalent server:

.. code:: console

   $ covalent start
   Covalent server has started at http://localhost:48008


Step 3: Run a Workflow
######################

Run this simple "Hello World" example to see Covalent in action.

Open a Jupyter notebook or Python console and create the following workflow:

.. code:: python

   import covalent as ct

   # Construct tasks as "electrons"
   @ct.electron
   def join_words(a, b):
       return ", ".join([a, b])

   @ct.electron
   def excitement(a):
       return f"{a}!"

   # Construct a workflow as "lattice"
   @ct.lattice
   def simple_workflow(a, b):
       phrase = join_words(a, b)
       return excitement(phrase)

   # Dispatch the workflow
   dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")


Step 4: View Results
####################

Use the Covalent GUI to view the workflow progress. Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

.. image:: ./../_static/hello_covalent_queue.png
  :align: center

Click on the dispatch ID to view the workflow graph:

.. image:: ./../_static/hello_covalent_graph.png
  :align: center
