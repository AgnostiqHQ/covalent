################
Deploying on AWS
################

Deploy Covalent in an AWS account with any ``x86``-based EC2 instance. Deploying on AWS Cloud enables you to scale your deployments based on compute needs.

As with the :doc:`Docker image<./deploy_with_docker>`, with each stable release we include a ready-to-use Amazon Machine Image (AMI) that is fully configured to start a Covalent server on instance boot.

To run Covalent on AWS, do the following:

Prerequisites
-------------

Have your `AWS account <https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html>`_ information ready, including:
azaszrfdrfdfr454rrfe432r
* The AWS subnet ID
* The ID of the security group you want to use
* Your EC2 authentication key-pair name

Procedure
---------

.. card:: 1. Query AWS Marketplace for the AMI ID.

    You can query directly from the console or via the ``aws cli`` command line tool. For example, the following CLI command queries details about the AMI released for version ``covalent==0.202.0``:

    .. code:: bash

        aws ec2 describe-images --owners Agnostiq --filter "Name=tag:Version,Values=0.202.0"

    .. note::  To get the current stable image of Covalent, use ``stable`` instead of ``latest``.

.. card:: 2. Once you have the AMI ID, launch an EC2 instance.

    You can launch an EC2 instance as follows:

    .. code:: bash

        aws ec2 run-instances --image-id <ami-id> --instance-type <instance-type> --subnet-id <subnet-id> -security-group-ids <security-group-id> --key-name <ec2-key-pair-name>

    where:

    ``ami-id``
        is the AMI ID you queried in the previous step.
    ``instance-type``
        is the EC2 instance type.
    ``subnet-id``
        is the AWS subnet ID.
    ``security-group-id``
        is the ID of the EC2 security group you want to assign to the instance.
    ``ec2-key-pair-name``
        is the name of the key pair you use to authenticate to EC2.

    For more complicated deployments, infrastructure-as-code tools such as `AWS CloudFormation <https://aws.amazon.com/cloudformation/>`_ and `Terraform <https://www.terraform.io/>`_ are available.
