################################
Installing Covalent with Systemd
################################

 We recommend that you *not* install Covalent directly at the system level as its Python version and package dependencies can conflict with those of the system. Instead, create a Python virtual environment with Covalent installed and manage Covalent with the ``systemd`` service. This approach prevents any Python conflicts.

.. note:: In these installation instructions, we assume ``Python3.8`` is available on the system and that all the commands are issued as ``root``.

To install Covalent on a Linux physical or virtual host with ``systemd``, do the following:

Prerequisites
-------------

On Debian/Ubuntu based systems, install the *virtualenv* Python module at the system level:

..code:: bash

    python3 -m pip install virtualenv

Procedure
---------

.. card:: 1. Create the Python virtual environment in which to install Covalent:

    .. code:: bash

       python3 -m virtualenv /opt/virtualenvs/covalent

.. card:: 2. Install Covalent in the virtual environment:

    .. code:: bash

        /opt/virtualenvs/covalent/bin/python -m pip install covalent

    This ensures that the latest release of Covalent along with all its dependencies are properly installed in the virtual environment.

.. card:: 3. If you plan to use the AWS executor plugins with your Covalent deployment, install the ``covalent-aws-plugins``:

    .. code:: bash

        /opt/virtualenvs/covalent/bin/python -m pip install 'covalent-aws-plugins[all]'

.. card:: 4. Create a ``systemd`` unit file for Covalent.

    Use the ``systemd`` ``Environment`` and ``EnvironmentFile`` directives to configure environment variables that determine Covalent's startup and runtime behavior.

    Customize the following sample ``covalent.service`` ``systemd`` unit file to your needs for hosting Covalent. On most Linux systems, this service file can be installed under ``/usr/lib/systemd/system``. For more information about the service file, see the ``systemd`` documentation `here <https://www.freedesktop.org/software/systemd/man/systemd.html>`_.

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

.. card:: 5. Configure a ``service`` account on the server with only the privileges required to ensure proper Covalent functionality.

    Running Covalent as the root user is *not* recommended; this compromises security on the server. For one thing, the Covalent GUI's built-in terminal provides a login shell as the Covalent user – so if the Covalent server is running as root, users have access to a root shell on the server.

.. card:: 6. To ensure that ``systemd`` invokes the Covalent server from within the virtual environment created earlier, set the ``VIRTUAL_ENV`` environment variable to the location of the virtual environment:

    .. code:: bash

       VIRTUAL_ENV=/opt/virtualenvs/covalent

    This ensures that the proper Python interpreter is used by Covalent at runtime.

.. card:: 7. (Optional) Customize Covalent-specific environment variables:

    Create the file specified in the In the ``[Service]`` directive ``EnvironmentFile`` location (in the above example, ``/etc/covalent/covalent.env``).

    Populate the file with Covalent-specific environment variables such as ``COVALENT_CACHE_DIR``, ``COVALENT_DATABASE``, ``COVALENT_SVC_PORT`` and so on to customize Covalent's runtime environment.

.. card::  8. Once all the settings have been configured, start Covalent:

    .. code:: bash

       systemctl daemon-reload
       systemclt start covalent.service

    .. note:: You only need to update ``systemd`` by executing the ``systemd daemon-reload`` command when a unit file is modified.

.. card:: 9. Check the status of the service at any time with:

    .. code:: bash

        systemctl status covalent

.. card:: 10. (Optional) Configure ``covalent.service`` to start on system bootup:

    .. code:: bash

       systemctl enable covalent.service


.. card:: 11. Once the service is running properly, connect to the Covalent GUI from a browser.

    Use the server hostname and port configured in the ``COVALENT_SVC_PORT`` environment variable. By default, Covalent start on port ``48008``.

.. card:: 12. If you need to stop the server, use:

    .. code:: bash

       systemctl stop covalent.service
