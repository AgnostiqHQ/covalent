===================================
Building and Installing from Source
===================================

This page describes how to build and install Covalent from source.

.. admonition:: Before you start

  Ensure you are using a compatible OS and Python version. See the :doc:`Compatibility <./compatibility>` page for supported Python versions and operating systems.


Building and Installing Covalent
################################

.. note::

   If you are upgrading Covalent from the previous stable release, refer to the :doc:`migration guide <./../version_migrations/index>` to preserve your data and avoid upgrade problems.


To download and install Covalent from source:

1. Clone the GitHub repo.

  .. code:: bash

     git clone git@github.com:AgnostiqHQ/covalent.git

2. The required packages are listed in ``covalent/requirements.txt``. Make sure you have them installed.

  .. code:: bash

    cd covalent
    pip install -r requirements.txt

3. Use the setup script to build and deploy Covalent.

  .. code:: bash

    cd covalent

    # Build the dashboard
    python setup.py webapp

    # Install using pip (-e is for developer mode)
    pip install -e .


Building the Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

To build the documentation locally:

1. The required packages are listed in ``covalent/doc/requirements.txt``. Make sure you have them installed.

   .. code:: bash

      cd covalent/doc
      pip install -r requirements.txt

2. Use the setup script to build the documentation:

.. code:: bash

   cd covalent
   python setup.py docs

The documentation is built into ``covalent/doc/build/html``. View the local documentation landing page at ``file:///covalent/doc/build/html/index.html``.

Validating the Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Covalent has been properly installed if the following returns without error:

.. code:: bash

   python -c "import covalent"
