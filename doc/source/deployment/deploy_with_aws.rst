Deployment on AWS
#################

Deploy Covalent in an AWS account with any ``x86``-based EC2 instance. Deploying on AWS Cloud enables you to scale your deployments based on compute needs.

As with the Docker image, with each stable release we include a ready-to-use Amazon Machine Image (AMI) that is fully configured to start a Covalent server on instance boot. Query AWS Marketplace for the AMI ID directly from the console or via the ``aws cli`` command line tool. For example, the following CLI command queries details about the AMI released for version ``covalent==0.202.0``:

.. code:: bash

    aws ec2 describe-images --owners Agnostiq --filter "Name=tag:Version,Values=0.202.0"

Once you have the AMI ID, you can launch an EC2 instance in your account as follows:

.. code:: bash

    aws ec2 run-instances --image-id <ami-id> --instance-type <instance-type> --subnet-id <subnet-id> -security-group-ids <security-group-id> --key-name <ec2-key-pair-name>

For more complicated deployments, infrastructure-as-code tools such as `AWS CloudFormation <https://aws.amazon.com/cloudformation/>`_ and `Terraform <https://www.terraform.io/>`_ are available.
