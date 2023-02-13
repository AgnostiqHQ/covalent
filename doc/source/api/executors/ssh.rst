.. _ssh_executor:

SSH Executor
"""""""""""""""""""""""""""

Executing tasks (electrons) via SSH in remote machine. This executor plugin interfaces Covalent with other machines accessible to the user over SSH. It is appropriate to use this plugin to distribute tasks to one or more compute backends which are not controlled by a cluster management system, such as computers on a LAN, or even a collection of small-form-factor Linux-based devices such as Raspberry Pis, NVIDIA Jetsons, or Xeon Phi co-processors.

To use this plugin with Covalent, simply install it using `pip`:

.. code:: shell

    pip install covalent-ssh-plugin


The following shows an example of how a user might modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_  to support this plugin:

.. code:: shell

    [executors.ssh]
    username = "user"
    hostname = "host.hostname.org"
    remote_dir = "/home/user/.cache/covalent"
    ssh_key_file = "/home/user/.ssh/id_rsa"


This setup assumes the user has the ability to connect to the remote machine using :code:`ssh -i /home/user/.ssh/id_rsa user@host.hostname.org` and has write-permissions on the remote directory :code:`/home/user/.cache/covalent` (if it exists) or the closest parent directory (if it does not).

Within a workflow, users can decorate electrons using the default settings:

.. code:: python

    import covalent as ct

    @ct.electron(executor="ssh")
    def my_task():
        import socket
        return socket.gethostname()


or use a class object to customize behavior within particular tasks:

.. code:: python

    executor = ct.executor.SSHExecutor(
        username="user",
        hostname="host2.hostname.org",
        remote_dir="/tmp/covalent",
        ssh_key_file="/home/user/.ssh/host2/id_rsa",
    )

    @ct.electron(executor=executor)
    def my_custom_task(x, y):
        return x + y



.. autoclass:: covalent.executor.SSHExecutor
    :members:
    :inherited-members:
