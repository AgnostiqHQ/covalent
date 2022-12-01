*************************
Covalent Deployment Guide
*************************

Covalent supports both local and remote installations to suit different uses cases and compute requirements. For quick prototyping and testing running ``Covalent`` locally
might be sufficient but for dispatching large compute intensive workflows which may require lots of CPU cores and memory, deploying ``Covalent`` as a **remote** server (cloud/on-prem) would be a better alternative. This way
users can still develop their workflows locally and dispatch them to the remote Covalent server for execution.

.. image:: ./covalent-self-hosted.svg
   :width: 800
   :alt: Covalent self hosted deployment

=========================
Deployment with Docker
=========================

Apart from installing ``Covalent`` locally within a Python virtual environment, users can also run Covalent as a docker container using the public images. The latest docker image for ``Covalent`` can be obtained as

.. code:: bash

    docker pull public.ecr.aws/covalent/covalent:latest


.. note::

    To obtain the stable image, the ``stable`` tag can be used instead of ``latest``

Covalent can then be started by running the container as follows

.. code:: bash

    docker container run -d --name covalent -p 48008:48008 public.ecr.aws/covalent/covalent:latest

This will start the container in detached mode and map port ``48008`` back out to host. To view the UI, users can then go to `http://localhost:48008 <http://localhost:48008>`_. Users can still configure Covalent that's running inside the container via environment variables.
The following table lists out all the supported environment variables that users can specify to customize Covalent's execution environment at start up.

.. list-table:: Covalent configuration environment variables
   :widths: 20 80
   :header-rows: 1

   * - Environment Variable
     - Description
   * - COVALENT_ROOT
     - Root directory for the ``covalent`` process
   * - COVALENT_CONFIG
     - Directory that ``covalent`` will search for its configuration file, ``covalent.conf``
   * - COVALENT_PLUGINS_DIR
     - Path where ``covalent`` will look to load any executor plugins installed
   * - COVALENT_DATABASE
     - Path to ``covalent``'s backend SQLite3 database
   * - COVALENT_LOGDIR
     - Path to ``covalent``'s log file
   * - COVALENT_CACHE_DIR
     - Directory to be used by ``covalent`` for storing temporary objects during runtime
   * - COVALENT_DATA_DIR
     - Path to ``covalent``'s database directory
   * - COVALENT_SVC_PORT
     - TCP port on which ``covalent`` will start running
   * - COVALENT_SERVER_IFACE_ANY
     - Boolean value to allow ``covalent`` to listen on all network interfaces on the host
   * - COVALENT_NUM_WORKERS
     - Number of Dask workers to start as part of Covalent's default cluster
   * - COVALENT_MEM_PER_WORKER
     - Memory limit for each dask worker
   * - COVALENT_THREADS_PER_WORKER
     - Number of threads to start each worker with


As an example users can start Covalent with 2 workers on port 8000 as follows

.. code:: bash

   docker container run --name covalent -p 8000:8000 -e COVALENT_NUM_WORKERS=2 -e COVALENT_SVC_PORT=8000 public.ecr.aws/covalent/covalent:latest


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

The recommended approach for running Covalent under systemd is to create a Python virtual environment with Covalent installed and then run the systemd service. This approach ensures that the system level Python settings are not altered and any potential Python package dependency conflicts are averted. In this guide, we assume ``Python3.8`` is available on the system and all the commands are carried out as the **root** user. We first being by creating the Python virtual environment in which Covalent will be subsequently installed

.. code:: bash

   python3 -m virtualenv /opt/virtualenvs/covalent

.. note::

   On Debian/Ubuntu based systems the **virtualenv** Python module can be installed at the system level via pip as follows ``python3 -m pip install virtualenv``

We can now install ``Covalent`` in this virtual environment as follows

.. code:: bash

   /opt/virtualenvs/covalent/bin/python -m pip install covalent


.. note::

   If users are looking to use the AWS executor plugins with their Covalent deployment the ``covalent-aws-plugins`` must be installed via ``/opt/virtualenvs/covalent/bin/python -m pip install 'covalent-aws-plugins[all]'``

This will ensure that the latest release of ``Covalent`` along with all its dependencies are properly installed in the virtual environment. We can now create a ``systemd`` unit file for Covalent and enable it to be managed by ``systemd``.
Systemd provides a convenient inferface to configure environment variables that will be exposed to the covalent server via the ``Environment`` and ``EnvironmentFile`` directives. We will leverage these interfaces to configure Covalent's startup and runtime behaviour. Users can use the following sample ``covalent.service`` systemd unit file and customize it for their needs when hosting Covalent themselves. On most linux systems, this service file can be installed under ``/usr/lib/systemd/system``. Users are encouraged to review the systemd documentation `here <https://www.freedesktop.org/software/systemd/man/systemd.html>`_.

.. code:: bash

   [Unit]
   Description=Covalent Dispatcher server
   After=network.target

   [Service]
   Type=forking
   Environment=VIRTUAL_ENV=/opt/virtualenvs/covalent
   Environment=PATH=/opt/virtualenvs/covalent/bin:$PATH
   Environment=HOME=/var/lib/covalent
   Environment=COVALENT_SERVER_IFACE_ANY=1
   EnvironmentFile=/etc/covalent/covalent.env
   ExecStartPre=-/opt/virtualenvs/covalent/bin/covalent stop
   ExecStart=/opt/virtualenvs/covalent/bin/covalent start
   ExecStop=/opt/virtualenvs/covalent/bin/covalent stop
   TimeoutStopSec=10

   [Install]
   WantedBy=multi-user.target


To ensure that when systemd invokes the ``Covalent`` server, its from within the virtual environment created earlier, we need to the set ``VIRTUAL_ENV`` environment variable to its proer value

.. code:: bash

   VIRTUAL_ENV=/opt/virtualenvs/covalent

Setting this variable to the location of the virtual environment is sufficient to ensure that the proper Python interpreter is used by Covalent at runtime. In the ``[Service]`` directive we set the ``EnvironmentFile`` location to ``/etc/covalent/covalent.env``. Users can optionally create this file and populate it with Covalent specific environment variables such as COVALENT_CACHE_DIR, COVALENT_DATABASE, COVALENT_SVC_PORT ... in order customize Covalent's runtime environment.

Once all the settings have been configured, Covalent can be started as follows

.. code:: bash

   systemctl daemon-reload
   systemclt start covalent.service


.. note::

   The status of the service can be inspected by ``systemctl status covalent``. The systemd ``daemon-reload`` command must be executed each time a unit file has been modified to notify systemd about the changes


The ``covalent.service`` can also be enabled to start on boot via systemd as follows

.. code:: bash

   systemctl enable covalent.service


Once the service is running properly, users can connect to the Covalent's UI from their browser by via their remote machines hostname and the port they configured Covalent to run on via the ``COVALENT_SVC_PORT`` environment variable. By default, Covalent start on port ``48008``.


====================
Deployment on AWS
====================

Users can deploy Covalent in their own AWS accounts with any ``x86`` based EC2 instance of their choice. This can allow users to vertically scale up their workloads as they can choose the compute instance type that is optimal for their use case. Similar to the docker image, we also regularly release Amazon Virtual Machine images (AMIs) with the latest version of Covalent pre-configured to run on instance boot. Users can query the Amazon Marketplace for the latest Covalent machine image provided by `Agnostiq` and use that for launching an EC2 instance. Steps to launch in EC2 instance from the AWS console can be found `here <https://docs.aws.amazon.com/efs/latest/ug/gs-step-one-create-ec2-resources.html>`_. Users can also use any infrastructure provisioning tool such as AWS CloudFormation or Terraform  to provision a Covalent server in their AWS accounts and setup the necessary policies as per their security requirements.
