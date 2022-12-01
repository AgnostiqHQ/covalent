*************************
Covalent Deployment Guide
*************************

Covalent supports both local and remote installations to suit different uses cases and compute requirements. For quick prototyping and testing running ``Covalent`` locally
might be sufficient but for dispatching large compute intensive workflows which may require lots of CPU cores and memory, deploying ``Covalent`` as a **remote** server (cloud/on-prem) would be a better alternative. This way
users can still develop their workflows locally and dispatch them to the remote Covalent server for execution.

.. toctree::
   :maxdepth: 2

   docker

==============================
On-prem deployment
==============================

The ``Covalent`` server can be installed and deployed on on-prem servers or virtual machines quite easily in order to centralize the deployment. This would enable users to host their Covalent servers on on-prem machines they may have access to or run them inside virtual machines. If the remote machines have `Docker <https://www.docker.com/>`_ support enabled then the deployment is trivally simple and amounts to simply pulling and running the Covalent container from our public registries. The deployment can be customized by following the steps outlined in :ref:`Deployment with Docker <Deployment with Docker>` section.


-----------------------
Deployment with Systemd
-----------------------
The Covalent server can also be installed and managed as a `systemd <https://systemd.io/>`_ service if desired. This can be a preferred approach if one would like to manage and administer the server via `systemd <https://systemd.io/>`_. There are several ways Covalent can be installed on a system and managed via systemd. For instance, users can directly install Covalent at the system level, install all the required plugins, create a ``covalent.service`` unit file and enable the service.

.. note::

   Installing Covalent at the system level is **NOT** recommended as its Python package dependencies can potentially conflict with system packages. Moreover, the system Python version may not be compatible with Covalent. Refer to our compatibility matrix to see all the support Python versions

The recommended approach for running Covalent under systemd is to create a Python virtual environment with Covalent installed and then run the systemd service. This approach ensures that the system level Python settings are not altered and any potential Python package dependency conflicts are averted. In this guide, we assume ``Python v3.8`` is available on the system and all the commands are carried out as the **root** user. We first being by creating the Python virtual environment in which Covalent will be subsequently installed

.. code:: bash

   python3 -m virtualenv /opt/virtualenvs/covalent
   export COVALENT_PYTHON=/opt/virtualenv/covalent/bin/python

.. note::

   We export the ``COVALENT_PYTHON`` environment variable for convenience as it will be used for executing any commands within the virtual environment.


We can now install ``Covalent`` in this virtual environment as follows

.. code:: bash

   $COVALENT_PYTHON -m pip install covalent


.. note::

   On Debian/Ubuntu based systems the **virtualenv** Python module can be installed at the system level via pip as follows ``python3 -m pip install virtualenv``


This will ensure that the latest release of ``Covalent`` along with all its dependencies are properly installed in the virtual environment. We can now create a ``systemd`` unit file for Covalent and enable it to be managed by ``systemd``.
Systemd provides a convenient inferface to configure environment variables that will be exposed to the process being managed via the ``Environment`` and ``EnvironmentFile`` directive. We will leverage these interfaces to configure Covalent's runtime behvaiour and environment by injecting variables.

To ensure that when systemd invokes the ``Covalent`` server, its from within the virtual environment created earlier, we need to the set ``VIRTUAL_ENV`` environment variable to its proer value

.. code:: bash

   VIRTUAL_ENV=/opt/virtualenvs/covalent

Setting this variable to the location where we first created the virtual environment will by sufficient to ensure that the Python used to run Covalent is properly sourced and all the ``site-packages`` are visible to the interpreter at runtime.




====================
Deployment on AWS
====================

Users can deploy Covalent in their own AWS accounts with any ``x86`` based EC2 instance of their choice. This can allow users to vertically scale up their workloads as they can choose the compute instance type that is optimal for their use case. There are several ways users can go about this as Covalent is already provided as a portable docker container. Users can deploy an EC2 virtual machine that is capable of running docker containers and simply follow the steps listed in :ref:`Deployment with Docker <Deployment with Docker>`
