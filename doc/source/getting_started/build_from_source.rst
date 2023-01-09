=============================
Building Covalent from Source
=============================

To download and install Covalent from source, follow the steps below.

.. card:: 1. Clone the GitHub repo:

    .. code:: bash

        $ cd <project_directory>
        $ git clone git@github.com:AgnostiqHQ/covalent.git

    where <project_directory> is the directory you choose to contain the project.

    .. note:: All file paths hereafter are relative to <project_directory>.

.. card:: 2. The Python packages required to build Covalent are listed in ``covalent/requirements.txt``. Make sure you have them installed:

    .. code:: bash

        $ cd covalent
        $ pip install -r requirements.txt

.. card:: 3. Use the setup script to build and deploy Covalent:

    .. code:: bash

        $ cd covalent

        # Build the dashboard
        $ python setup.py webapp

        # Install using pip (-e is for developer mode)
        $ pip install -e .


Building the Documentation
--------------------------

Optionally, you can build the documentation locally. Follow these steps:

.. card:: 1. The required packages are listed in ``covalent/doc/requirements.txt``. Make sure you have them installed:

    .. code:: bash

        $ cd covalent/doc
        $ pip install -r requirements.txt

.. card:: 2. Use the setup script to build the documentation:

    .. code:: bash

        $ cd covalent
        $ python setup.py docs

The script builds the documentation in ``covalent/doc/build/html``. View the local documentation landing page in your browser at ``file:///covalent/doc/build/html/index.html``.

Validating the Installation
---------------------------

Optionally, validate the installation.

.. card:: Covalent has been properly installed if the following returns without error:

    .. code:: bash

       $ python -c "import covalent"
