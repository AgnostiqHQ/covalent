.. _awsecs_executor:

🔌 AWS ECS Executor
"""""""""""""""""""""""""""

.. image:: AWS_ECS.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Elastic Container Service (ECS).
This executor plugin is well suited for low to medium compute intensive electrons with modest memory requirements. Since AWS ECS
offers very quick spin up times, this executor is a good fit for workflows with a large number of independent tasks that can
be dispatched simultaneously.

1. Installation
###############

To use this plugin with Covalent, simply install it using pip:

.. code-block:: shell

    pip install covalent-ecs-plugin

2. Usage Example
################

This is an example of how a workflow can be constructed to use the AWS ECS executor. In the example, we join two words to form a phrase
and return an excited phrase.

.. code-block:: python

    import covalent as ct

    executor = ct.executor.ECSExecutor(
        s3_bucket_name="covalent-fargate-task-resources",
        ecr_repo_name="covalent-fargate-task-images",
        ecs_cluster_name="covalent-fargate-cluster",
        ecs_task_family_name="covalent-fargate-tasks",
        ecs_task_execution_role_name="ecsTaskExecutionRole",
        ecs_task_role_name="CovalentFargateTaskRole",
        ecs_task_subnet_id="subnet-871545e1",
        ecs_task_security_group_id="sg-0043541a",
        ecs_task_log_group_name="covalent-fargate-task-logs",
        vcpu=1,
        memory=2,
        poll_freq=10,
        )


    @ct.electron(executor=executor)
    def join_words(a, b):
        return ", ".join([a, b])


    @ct.electron(executor=executor)
    def excitement(a):
        return f"{a}!"


    @ct.lattice
    def simple_workflow(a, b):
        phrase = join_words(a, b)
        return excitement(phrase)


    dispatch_id = ct.dispatch(simple_workflow)("Hello", "World")
    result = ct.get_result(dispatch_id, wait=True)

    print(result)

During the execution of the workflow, one can navigate to the UI to see the status of the workflow. Once completed, the above script
should also output the result:

.. code-block:: shell

    Hello, World

In order for the above workflow to run successfully, one has to provision the required AWS resources as mentioned in :ref:`required_aws_resources`.

3. Overview of configuration
############################

The following table shows a list of all input arguments including the required arguments to be supplied when instantiating the executor:

.. list-table::
   :widths: 25 25 25 50
   :header-rows: 1

   * - Config Value
     - Is Required
     - Default
     - Description
   * - credentials
     - No
     - `~/.aws/credentials`
     - The path to the AWS credentials file
   * - profile
     - No
     - default
     - The AWS profile used for authentication
   * - s3_bucket_name
     - No
     - covalent-fargate-task-resources
     - The name of the S3 bucket where objects are stored
   * - ecr_repo_name
     - No
     - covalent-fargate-task-images
     - The name of the ECR repository where task images are stored
   * - ecs_cluster_name
     - No
     - covalent-fargate-cluster
     - The name of the ECS cluster on which tasks run
   * - ecs_task_family_name
     - No
     - covalent-fargate-tasks
     - The name of the ECS task family for a user, project, or experiment.
   * - ecs_task_execution_role_name
     - No
     - CovalentFargateTaskRole
     - The IAM role used by the ECS agent
   * - ecs_task_role_name
     - No
     - CovalentFargateTaskRole
     - The IAM role used by the container during runtime
   * - ecs_task_subnet_id
     - Yes
     - An empty string
     - Valid subnet ID
   * - ecs_task_security_group_id
     - Yes
     - An empty string
     - Valid security group ID
   * - ecs_task_log_group_name
     - No
     - covalent-fargate-task-logs
     - The name of the CloudWatch log group where container logs are stored
   * - vcpu
     - No
     - 0.25
     - The number of vCPUs available to a task
   * - memory
     - No
     - 0.5
     - The memory (in GB) available to a task
   * - poll_freq
     - No
     - 10
     - The frequency (in seconds) with which to poll a submitted task
   * - cache_dir
     - No
     - `/tmp/covalent`
     - The cache directory used by the executor for storing temporary files

The following snippet shows how users may modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ to provide
the necessary input arguments to the executor:


.. code-block:: shell

    [executors.ecs]
    credentials = "~/.aws/credentials"
    profile = "default"
    s3_bucket_name = "covalent-fargate-task-resources"
    ecr_repo_name = "covalent-fargate-task-images"
    ecs_cluster_name = "covalent-fargate-cluster"
    ecs_task_family_name = "covalent-fargate-tasks"
    ecs_task_execution_role_name = "ecsTaskExecutionRole"
    ecs_task_role_name = "CovalentFargateTaskRole"
    ecs_task_subnet_id = "<my-subnet-id>"
    ecs_task_security_group_id = "<my-security-group-id>"
    ecs_task_log_group_name = "covalent-fargate-task-logs"
    vcpu = 0.25
    memory = 0.5
    cache_dir = "/tmp/covalent"
    poll_freq = 10

Within a workflow, users can use this executor with the default values configured in the configuration file as follows:

.. code-block:: python

    import covalent as ct

    @ct.electron(executor="ecs")
    def task(x, y):
        return x + y


Alternatively, users can customize this executor entirely by providing their own values to its constructor as follows:

.. code-block:: python

    import covalent as ct
    from covalent.executor import ECSExecutor

    ecs_executor = ECSExecutor(
        credentials="my_custom_credentials",
        profile="my_custom_profile",
        s3_bucket_name="my_s3_bucket",
        ecr_repo_name="my_ecr_repo",
        ecs_cluster_name="my_ecs_cluster",
        ecs_task_family_name="my_custom_task_family",
        ecs_task_execution_role_name="myCustomTaskExecutionRole",
        ecs_task_role_name="myCustomTaskRole",
        ecs_task_subnet_id="my-subnet-id",
        ecs_task_security_group_id="my-security-group-id",
        ecs_task_log_group_name="my-task-log-group",
        vcpu=1,
        memory=2,
        cache_dir="/home/<user>/covalent/cache",
        poll_freq=10,
        )

    @ct.electron(executor=ecs_executor)
    def task(x, y):
        return x + y

.. _required_aws_resources:

4. Required AWS Resources
##########################

This executor uses different AWS services (`S3 <https://aws.amazon.com/s3/>`_, `ECR <https://aws.amazon.com/ecr/>`_, `ECS <https://aws.amazon.com/ecs/>`_, and `Fargate <https://aws.amazon.com/fargate/>`_) to successfully run a task. In order for the executor to work end-to-end, the following resources need to be configured
either with `Terraform <https://www.terraform.io/>`_ or manually provisioned on the `AWS Dashboard <https://aws.amazon.com/>`_

.. list-table::
    :widths: 25 25 50
    :header-rows: 1

    * - Resource
      - Config Name
      - Description
    * - IAM Role
      - ecs_task_execution_role_name
      - The IAM role used by the ECS agent
    * - IAM Role
      - ecs_task_role_name
      - The IAM role used by the container during runtime
    * - S3 Bucket
      - s3_bucket_name
      - The name of the S3 bucket where objects are stored
    * - ECR repository
      - ecr_repo_name
      - The name of the ECR repository where task images are stored
    * - ECS Cluster
      - ecs_cluster_name
      - The name of the ECS cluster on which tasks run
    * - ECS Task Family
      - ecs_task_family_name
      - The name of the task family that specifies container information for a user, project, or experiment
    * - VPC Subnet
      - ecs_task_subnet_id
      - The ID of the subnet where instances are created
    * - Security group
      - ecs_task_security_group_id
      - The ID of the security group for task instances
    * - Cloudwatch log group
      - ecs_task_log_group_name
      - The name of the CloudWatch log group where container logs are stored
    * - CPU
      - vCPU
      - The number of vCPUs available to a task
    * - Memory
      - memory
      - The memory (in GB) available to a task


The following IAM roles and policies must be properly configured so that the executor has all the necessary permissions to interact with the different AWS services:

#. ``ecs_task_execution_role_name`` is the IAM role used by the ECS agent
#. ``ecs_task_role_name`` is the IAM role used by the container during runtime

If omitted, these IAM role names default to ``ecsTaskExecutionRole`` and ``CovalentFargateTaskRole``, respectively.
The IAM policy attached to the ``ecsTaskExecutionRole`` is the following:

.. dropdown:: ECS Task Execution Role IAM Policy

    .. code:: json

        {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]
    }

These policies allow the service to download container images from ECR so that the tasks can be executed on an ECS
cluster. The policy attached to the ``CovalentFargateTaskRole`` is as follows

.. dropdown:: AWS Fargate Task Role IAM Policy

    .. code:: json

        {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "braket:*",
                "Resource": "*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::covalent-fargate-task-resources/*",
                    "arn:aws:s3:::covalent-fargate-task-resources"
                ]
            }
        ]
    }

Users can provide their custom IAM roles/policies as long as they respect the permissions listed in the above documents.
For more information on how to create IAM roles and attach policies in AWS, refer to `IAM roles <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html>`_.

The executor also requires a proper networking setup so that the containers can be properly launched into their respective
subnets. The executor requires that the user provide a ``subnet`` ID and a ``security group`` ID prior to using the executor
in a workflow.

The executor uses `Docker <https://www.docker.com/>`_ to build container images with the task function code baked into the
image. The resulting image is pushed into the elastic container registry provided by the user. Following this,
an ECS task definition using the user provided arguments is registered and the corresponding task container is launched.
The output from the task is uploaded to the S3 bucket provided by the user and parsed to obtain the result object.
In order for the executor to properly run and build images, users must have `Docker installed <https://www.docker.com/get-started/>`_ and properly
configured on their machines.
