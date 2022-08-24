.. _awsec2_executor:

🔌 AWS EC2 Executor
"""""""""""""""""""""""""""

.. image:: AWS_EC2.jpg

This executor plugin interfaces Covalent with an EC2 instance over SSH. This plugin is appropriate for executing workflow tasks on an instance that has been auto-provisioned and configured by the plugin.

To use this plugin with Covalent, simply install it using `pip`:

.. code:: shell

    pip install covalent-ec2-plugin

Users will also need to have `Terraform <https://www.terraform.io/downloads>`_ installed on their local machine in order to use this plugin.
The following shows an example of how a user might modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_  to support this plugin:

.. code:: shell

    [executors.ec2]
    username = "ubuntu"
    profile = "default"
    credentials_file = "/home/user/.aws/credentials"
    key_name = "ssh_key"
    ssh_key_file = "/home/user/.ssh/ssh_key.pem"


This configuration assumes that the user has created a private key file for connecting to the instance via SSH that is stored on their local machine at `/home/user/.ssh/ssh_key.pem`. The configuration also assumes that the user uses the default AWS profile and credentials file located at `/home/user/.aws/credentials` to authenticate to their AWS account.


Within a workflow, users can decorate electrons using the minimal default settings:

.. code:: python

    import covalent as ct

    @ct.electron(executor="ec2")
    def my_task():
        import socket
        return socket.get_hostname()



or use a class object that makes use of a custom AWS user profile to deploy a specific instance type within a specific subnet in a VPC:

.. code:: python

    executor = ct.executor.EC2Executor(
        username="ubuntu",
        ssh_key_file="/home/user/.ssh/ssh_key.pem",
        key_name="ssh_key"
        instance_type="t2.micro",
        volume_size="8GiB",
        ami="amzn-ami-hvm-*-x86_64-gp2",
        vpc="vpc-07bdd9ca40c4c50a7",
        subnet="subnet-0a0a7f2a7532383c3",
        profile="custom_user_profile",
        credentials_file="~/.aws/credentials"
    )

    @ct.electron(executor=executor)
    def my_custom_task(x, y):
        return x + y



.. autoclass:: covalent.executor.EC2Executor
    :members:
    :inherited-members:
