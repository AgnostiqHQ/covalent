===============
Getting Started
===============

Covalent is developed using Python 3.8 on Linux and macOS.  See the :doc:`Compatibility <./compatibility>` page for further details on Python versions and operating systems which support Covalent. To set up Python on your computer, refer to the official `Python for Beginners <https://www.python.org/about/gettingstarted/>`_ page.

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

   Installation via Conda is currently only supported for Linux. Sometimes Conda can have trouble resolving packages. Use the flag :code:`--override-channels` to speed things up.

Docker Install
--------------

Covalent can also run in Docker containers instead of :code:`covalent start`:

.. code:: bash

   git clone git@github.com:AgnostiqHQ/covalent.git
   cd covalent
   docker compose up -d

.. note::

   The Docker image for Covalent is still being tested. Please open an issue on `GitHub <https://github.com/AgnostiqHQ/covalent/issues>`_ if you encounter unexpected behavior.

Install From Source
--------------------

Covalent can also be downloaded and installed from source:

.. code:: bash

   git clone git@github.com:AgnostiqHQ/covalent.git
   cd covalent

   # Build dashboard
   python setup.py webapp

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


Migration Guide from 0.3x
~~~~~~~~~~~~~~~~~~~~

If you are running covalent version 0.3x you can upgrade to covalent version 0.8x as follows.

By running the following commands you can verify your covalent python as well as stop covalent and purge any config files present.

.. code:: bash

   $ pip show cova | grep Version
   Version: 0.32.3
   $ covalent purge
   Covalent server has stopped.
   Covalent server files have been purged.

You can install the an 0.8x version of covalent by using pip.

.. code:: bash

   $ pip install cova==0.89.2 --upgrade
   $ pip show cova | grep Version
   Version: 0.89.2

You should now be able to start the updated covalent server using :code:`covalent start` as specified in the guide below.

Start the Server
#################

Use the Covalent CLI tool to manage the Covalent server. The following commands will help you get started.

.. code:: console

   $ covalent --help
   Usage: covalent [OPTIONS] COMMAND [ARGS]...

      Covalent CLI tool used to manage the servers.

   Options:
      -v, --version  Display version information.
      --help         Show this message and exit.

   Commands:
      config   Get and set the configuration of services.
      logs
      purge    Shutdown server and delete the cache and config settings.
      restart  Restart the server(s).
      start
      status   Return the statuses of the server(s).
      stop     Stop the server(s).

Start the Covalent server:

.. code:: console

   $ covalent start
   Started Supervisord process 25109.

   Supervisord is running in process 25109.
   covalent:data                     STARTING
   covalent:dispatcher               STARTING
   covalent:dispatcher_mq_consumer   STARTING
   covalent:nats                     STARTING
   covalent:queuer                   STARTING
   covalent:results                  STARTING
   covalent:runner                   STARTING
   covalent:ui                       STARTING

Optionally, confirm the server is running:

.. code:: console

   $ covalent status
   Supervisord is running in process 25109.
   covalent:data                     RUNNING   pid 25660, uptime 0:16:03
   covalent:dispatcher               RUNNING   pid 25658, uptime 0:16:03
   covalent:dispatcher_mq_consumer   RUNNING   pid 25663, uptime 0:16:03
   covalent:nats                     RUNNING   pid 25656, uptime 0:16:03
   covalent:queuer                   RUNNING   pid 25657, uptime 0:16:03
   covalent:results                  RUNNING   pid 25662, uptime 0:16:03
   covalent:runner                   RUNNING   pid 25659, uptime 0:16:03
   covalent:ui                       RUNNING   pid 25661, uptime 0:16:03

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

Navigate to the Covalent UI at `<http://localhost:8000>`_ to see your workflow in the queue:

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
   Supervisord is running in process 25109.
   covalent:dispatcher_mq_consumer: stopped
   covalent:data: stopped
   covalent:nats: stopped
   covalent:ui: stopped
   covalent:results: stopped
   covalent:queuer: stopped
   covalent:dispatcher: stopped
   covalent:runner: stopped

Read more about how Covalent works on the Covalent :doc:`concepts <../concepts/concepts>` page.
