============
How to manage the Covalent services.
============

In order to dispatch lattices for execution, the user needs to start Covalent's services. Covalent provides a Command Line Interface (CLI) to start, stop or check the status of the services using the terminal. In order to start the services, the :code:`start` command can be used in a shell.

.. code-block:: sh

    $ covalent start
    Checking if covalent has started (this may take a few seconds)...
    Started Supervisord process 27477.

    Supervisord is running in process 27477.
    covalent:data                     RUNNING   pid 27548, uptime 0:00:03
    covalent:dispatcher               RUNNING   pid 27546, uptime 0:00:03
    covalent:dispatcher_mq_consumer   RUNNING   pid 27551, uptime 0:00:03
    covalent:nats                     RUNNING   pid 27552, uptime 0:00:03
    covalent:queuer                   RUNNING   pid 27544, uptime 0:00:03
    covalent:results                  RUNNING   pid 27550, uptime 0:00:03
    covalent:runner                   RUNNING   pid 27547, uptime 0:00:03
    covalent:ui                       RUNNING   pid 27549, uptime 0:00:03

.. note:: By default, the user interface uses port 8000. Navigate to `<http://localhost:8000>`_ to view the user interface. The other service defaults are as follows: the queue service uses port 8001, the dispatcher service uses port 8002, the runner service uses port 8003, the data service uses port 8004, and the results service uses port 8005.

The user can check the status of services using the :code:`status` command.

.. code-block:: sh

    $ covalent status
    Supervisord is running in process 27477.
    covalent:data                     RUNNING   pid 27548, uptime 0:11:08
    covalent:dispatcher               RUNNING   pid 27546, uptime 0:11:08
    covalent:dispatcher_mq_consumer   RUNNING   pid 27551, uptime 0:11:08
    covalent:nats                     RUNNING   pid 27552, uptime 0:11:08
    covalent:queuer                   RUNNING   pid 27544, uptime 0:11:08
    covalent:results                  RUNNING   pid 27550, uptime 0:11:08
    covalent:runner                   RUNNING   pid 27547, uptime 0:11:08
    covalent:ui                       RUNNING   pid 27549, uptime 0:11:08

or by navigating to the Covalent service dashboard at `<http://localhost:9001>`_. In order to stop the services, use the :code:`stop` command.

.. code-block:: sh

    $ covalent stop
    Supervisord is running in process 27477.
    covalent:dispatcher_mq_consumer: stopped
    covalent:nats: stopped
    covalent:queuer: stopped
    covalent:data: stopped
    covalent:dispatcher: stopped
    covalent:runner: stopped
    covalent:ui: stopped
    covalent:results: stopped

Covalent also can restart the services:

.. code-block:: sh

    $ covalent restart
    Supervisord already running in process 27477.
    covalent:dispatcher_mq_consumer: stopped
    covalent:nats: stopped
    covalent:data: stopped
    covalent:queuer: stopped
    covalent:ui: stopped
    covalent:runner: stopped
    covalent:dispatcher: stopped
    covalent:results: stopped
    covalent:nats: started
    covalent:queuer: started
    covalent:dispatcher: started
    covalent:runner: started
    covalent:data: started
    covalent:ui: started
    covalent:results: started
    covalent:dispatcher_mq_consumer: started

The ports and addresses of the services may be configured by modifying the Covalent configuration as discussed in the :doc:`configuration customization<../config/customization>` how-to guide.

Lastly, the config file can be reset using the following command:

.. code-block:: sh

    $ covalent purge
    Supervisord is running in process 27477.
    covalent:dispatcher_mq_consumer: stopped
    covalent:nats: stopped
    covalent:queuer: stopped
    covalent:data: stopped
    covalent:ui: stopped
    covalent:runner: stopped
    covalent:dispatcher: stopped
    covalent:results: stopped

    Covalent server has stopped.
    Covalent server files have been purged.

This is useful when the user wishes to uninstall Covalent and reset all settings to defaults upon reinstallation.

.. warning::

    This will also delete all directories referenced in the config file (logs, caches) with the exception of the results directory.
