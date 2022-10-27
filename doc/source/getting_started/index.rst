===============
Getting Started
===============

Covalent is a Pythonic workflow tool for data scientists, AI/ML researchers, and anyone who needs a way to run experiments on limited or expensive computing resources. Such resources can include quantum computers, HPC clusters, GPU arrays, and cloud services. Covalent manages workflows in heterogeneous environments that contain any or all of these advanced platforms.

Covalent enables you to:
* Isolate operations that don't require advanced compute resources so you can run them on commonly available hardware;
* Test individual functions or groups of functions on local hardware or inexpensive servers before committing them to advanced hardware;
* Manage experiments and view results in a browser-based GUI;
* Automate and manage workflows from a Jupyter notebook;
* Parallelize independent computations to accelerate job completion;
* Bring existing code into Covalent without extensive refactoring.

Covalent is developed in Python 3.8 on Linux and macOS.  See the :doc:`Compatibility <./compatibility>` page for supported Python versions and operating systems. To set up Python on your computer, refer to the official `Python for Beginners <https://www.python.org/about/gettingstarted/>`_ page.

Installing Covalent
###################

.. note::

   If you are upgrading Covalent from the previous stable release, refer to the :doc:`migration guide <./../version_migrations/index>` to preserve your data and avoid upgrade problems.

You can install Covalent using the Python package manager, using Conda, or by building and installing from source.

Pip Install
~~~~~~~~~~~

The easiest way to install Covalent is to use Pip, the Python package manager.

.. note::

   If you have previously used Covalent, uninstall the Covalent Dask plugin by running :code:`pip uninstall covalent-dask-plugin`. The plugin has been folded into Covalent and is no longer maintained separately.

To install using Pip:

.. code:: bash

   pip install covalent


Conda Install
~~~~~~~~~~~~~

You can install Covalent as a package in a Conda environment:

.. code:: bash

   conda install -c agnostiq covalent

.. note::

   Conda installation is currently only supported for Linux. Sometimes Conda can have trouble resolving packages. Use the flag :code:`--override-channels` to speed up installation.

   On Mac, you can use Conda to manage your environment but must use Pip to install Covalent.

Install From Source
~~~~~~~~~~~~~~~~~~~

You can download and install Covalent from source:

.. code:: bash

   git clone git@github.com:AgnostiqHQ/covalent.git
   cd covalent

   # Build dashboard
   python setup.py webapp

   # Either:
   # 1. Install using pip (-e is for developer mode)
   pip install -e .

   # - or -
   # 2. Build and install using Conda (takes 10-15 mins)
   conda build .
   conda install -c local covalent

To build the documentation locally:

.. code:: bash

   python setup.py docs


Validating the Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Covalent has been properly installed if the following returns without error:

.. code:: bash

   python -c "import covalent"

Starting the Server
###################

Start the Covalent server:

.. code:: console

   $ covalent start
   Covalent server has started at http://localhost:48008

Managing the Server
~~~~~~~~~~~~~~~~~~~

Use the Covalent CLI tool to manage the Covalent server. You can start and stop the server, view its status, and see the server logs.

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

Navigate to the Covalent UI by entering the address, http://localhost:48008, into your web browser.  This is where dispatched jobs will appear.


Running a Workflow
##################

Run this simple "Hello World" example to see Covalent in action.

Before starting, ensure that you have installed Covalent, verified the installation, and started the Covalent server.

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

Navigate to the Covalent UI at `<http://localhost:48008>`_ to see your workflow in the queue:

|

.. image:: hello_covalent_queue.png
   :align: center


Click on the dispatch ID to view the workflow graph:

|

.. image:: hello_covalent_graph.png
   :align: center


While the workflow is being processed by the dispatch server, you can terminate the Jupyter kernel or Python console process without losing access to the results. Make sure the Covalent server remains in the "running" state while you have running workflows.

When the workflow has completed, you can start a new session and query the results:

.. code:: python

   import covalent as ct

   # Copy the dispatch ID from the UI
   dispatch_id = "12345678-1234-1234-1234-123456789abc"
   result_string = ct.get_result(dispatch_id).result

When you are done using Covalent to run workflows, stop the server:

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
