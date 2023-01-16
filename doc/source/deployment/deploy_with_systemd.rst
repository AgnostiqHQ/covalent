################################
Installing Covalent with Systemd
################################

.. note:: In these installation instructions, we assume :code:`Python3.8` is available on the system and that all the commands are issued as :code:`root`.

To install Covalent on a Linux physical or virtual host with :code:`systemd`, do the following:

.. card:: 1. Use Pip to install the Covalent server and libraries locally.


    Type the following in a terminal window:

    .. code:: bash

        $ pip install covalent



.. card:: 2. Start the Covalent server.


    In the terminal window, type:

    .. code:: console

        $ covalent start
        Covalent server has started at http://localhost:48008




.. card:: 1. Create the Python virtual environment in which to install Covalent.

.. code:: bash

   python3 -m virtualenv /opt/virtualenvs/covalent

.. note::

   On Debian/Ubuntu based systems the **virtualenv** Python module can be installed at the system level via pip as follows ``python3 -m pip install virtualenv``

We can now install Covalent in this virtual environment as follows

.. code:: bash

   /opt/virtualenvs/covalent/bin/python -m pip install covalent


.. note::

   If users are looking to use the AWS executor plugins with their Covalent deployment the ``covalent-aws-plugins`` must be installed via ``/opt/virtualenvs/covalent/bin/python -m pip install 'covalent-aws-plugins[all]'``

This will ensure that the latest release of Covalent along with all its dependencies are properly installed in the virtual environment. We can now create a ``systemd`` unit file for Covalent and enable it to be managed by ``systemd``.
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


To ensure that when systemd invokes the Covalent server, its from within the virtual environment created earlier, we need to the set ``VIRTUAL_ENV`` environment variable to its proper value

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


Once the service is running properly, users can connect to the Covalent's UI from their browser by via their remote machines hostname and the port they configured Covalent to run on via the ``COVALENT_SVC_PORT`` environment variable. By default, Covalent start on port ``48008``. The server can be stopped using systemd as follows

.. code:: bash

   systemctl stop covalent.service


.. warning::

   Running Covalent as the root user is **NOT** recommended as it can have several security implications for the remote server. If possible, users must configure a ``service`` account on the system with just the right amount of privileges to ensure proper Covalent functionality. The Covalent UI has an in-built terminal for convenience and it present a login shell as the Covalent user i.e. if the Covalent server is running as root, then users will have access to a root shell on the server. This can potentially have major security implications, thus proper UNIX security polices and best practices must be followed when self-hosting Covalent on remote servers
