===============
Getting Started
===============

Covalent is developed using Python 3.8 on Linux and macOS.  Other versions or operating systems may be supported but have not been rigorously tested. To set up Python on your computer, refer to the official `Python for Beginners <https://www.python.org/about/gettingstarted/>`_ page.

Installation
############

Installation Methods
~~~~~~~~~~~~~~~~~~~~

Pip Install
-----------

The easiest way to install Covalent is using the PyPI package manager:

.. code:: bash

   pip install cova

Conda Install
-------------

Users can also install Covalent as a package in a Conda environment:

.. code:: bash

   conda install -c agnostiq covalent

.. note::

   Sometimes Conda can have trouble resolving packages. Use the flag :code:`--override-channels` to speed things up.

Docker Install
--------------

Covalent is also provided as a Docker image. This image can be used as a developer environment or simply to run the Covalent dispatch server in a container:

.. code:: bash

   docker pull public.ecr.aws/i9y7r1d8/covalent

   # Run the container as a developer environment
   docker run -it --rm covalent bash

   # Run the container as a dispatch server
   docker run -d -p 48008 covalent

.. note::

   The Docker image for Covalent is still being tested. Please open an issue on `GitHub <https://github.com/AgnostiqHQ/covalent/issues>`_ if you encounter unexpected behavior.

Install From Source
--------------------

Covalent can also be downloaded and installed from source:

.. code:: bash

   git clone git@github.com:AgnostiqHQ/covalent.git
   cd covalent

   # Install using setuptools, or...
   python setup.py

   # Install using pip (-e for developer mode), or...
   pip install -e .

   # Build and install using Conda (10-15 mins)
   conda build .
   conda install -c local covalent

The documentation can also easily be built locally:

.. code:: bash

   python setup.py docs

.. note::

   Users who wish to use the :code:`draw` functionality outside of the UI may also wish to install :code:`graphviz` and :code:`pygraphviz`, either using Conda or Linux package managers. This is not required to use Covalent.

Validate the Installation
~~~~~~~~~~~~~~~~~~~~~~~~~

You can validate Covalent has been properly installed if the following returns without error:

.. code:: bash

   python -c "import covalent"

Start the Servers
#################

Covalent uses two local services: a dispatcher server and a UI server. These servers are managed by the Covalent CLI tool. The following are some useful commands to help you get started.

.. code:: console

   $ covalent --help
   Usage: covalent [OPTIONS] COMMAND [ARGS]...

     Covalent CLI tool used to manage the dispatcher and UI servers.

   Options:
     -v, --version  Display version information.
     --help         Show this message and exit.

   Commands:
     purge    Delete the cache and config settings.
     restart  Restart the dispatcher and/or UI servers.
     start    Start the dispatcher and/or UI servers.
     status   Query the status of the dispatcher and UI servers.
     stop     Stop the dispatcher and/or UI servers.

Start the Covalent server:

.. code:: console

   $ covalent start
   Covalent dispatcher server has started at http://0.0.0.0:48008
   Covalent UI server has started at http://0.0.0.0:47007

Optionally, confirm the servers are running:

.. code:: console

   $ covalent status
   Covalent dispatcher server is running at http://0.0.0.0:48008.
   Covalent UI server is running at http://0.0.0.0:47007.

Now, navigate to the Covalent UI by entering the address into your web browser.  This is where dispatched jobs will appear.

Hello, Covalent!
################

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

Navigate to the Covalent UI at `<http://0.0.0.0:47007>`_ to see your workflow in the queue:

|

.. image:: hello_covalent_queue.png
   :align: center

|

.. warning::
   In some browsers and operating systems, the address `0.0.0.0` does not resolve to localhost. If you experience issues, try instead navigating to `<http://localhost:47007>`_.

Click on the dispatch ID to view the workflow graph:

|

.. image:: hello_covalent_graph.png
   :align: center


While the workflow is being processed by the dispatch server, you are free to terminate the Jupyter kernel or Python console process without losing access to the results. Make sure the Covalent servers remain in the "running" state while you have running workflows.

When the workflow has completed, you can start a new session and query the results:

.. code:: python

   import covalent as ct

   dispatch_id = "8a7bfe54-d3c7-4ca1-861b-f55af6d5964a"
   result_string = ct.get_result(dispatch_id).result

When you are done using Covalent, stop the servers:

.. code:: console

   $ covalent stop
   Covalent dispatcher server has stopped.
   Covalent UI server has stopped.

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
