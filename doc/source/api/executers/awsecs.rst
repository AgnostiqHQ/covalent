.. _awsecs_executor:

🔌 AWS ECS Executor
"""""""""""""""""""""""""""

.. image:: AWS_ECS.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Elastic Container service (ECS).
This executor plugin is well suited for low to medium compute intensive electrons with modest memory requirements. Since the AWS ECS,
services offers very quick spin up times, this executor is a good fit for workflows with a large number of independent tasks that can
be dispatched simultaneously.

Since this is a cloud executor, proper IAM credentials, permissions and roles must be configured prior to using this executor.
This executor uses different AWS services (S3, ECR and ECS Fargate) to successfully run a task. To this end the IAM roles and policies must be
properly configured so that the executor has all the necessary permissions to interact with the different AWS services.

The executor uses multiple IAM roles configured with different policies each during execution.

#. ``ecs_task_execution_role_name`` is the IAM role used by the Elastic container service agent
#. ``ecs_task_role_name`` is the IAM role used by the container during runtime

If omitted, these IAM role names default ``ecsTaskExecutionRole`` and ``CovalentFargateTaskRole`` respectively.
The IAM policy attached to the ``ecsTaskExecutionRole`` is the following

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

These policies allow the service to download container images from ECR so that the tasks can be executed on a ECS
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

User's can provide their custom IAM roles/policies as long as they respect the permissions listed in the above documents.
The executor also requires a proper networking setup so that the containers can be properly launched into their respective
subnets. The executor requires that the user provide a ``subnet`` and a ``security group`` ID prior to using the executor
in a workflow.

This executor uses `Docker <https://www.docker.com/>`_ to build container images with the task function code baked into the
image. The resulting image is pushed into the elastic container registry provided by the user. Following this,
an ECS task defintion using the user provided arguments is registered and the corresponding task container is launched.
The output from the task is uploaded to the S3 bucket provided by the user and parsed to obtain the result object.
In order for the executor to properly run and build images, users must have Docker installed and properly
configured on their machines.

This executor plugin can be installed via ``pip``

.. code:: bash

    pip install covalent-ecs-plugin


Users can configure this executor by providing their custom configuration values in Covalent's `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ as follows

.. code:: bash

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

Note that the parameters ``ecs_task_subnet_id`` and ``ecs_task_security_group_id`` are required parameters and must
be provided by the user prior to using this executor in their workflows.

Within a workflow, users can then decorate their tasks as

.. code:: python

    import covalent as ct

    @ct.electron(executor="ecs")
    def my_task(x, y):
        return x + y

Using this executor in this manner will cause it to parse the values from the configuration file during runtime.

.. autoclass:: covalent.executor.ECSExecutor
    :members:
    :inherited-members:
