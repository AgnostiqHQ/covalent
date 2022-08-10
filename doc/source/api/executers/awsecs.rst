.. _awsecs_executor:

🔌 AWS ECS Executor
"""""""""""""""""""""""""""

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Elastic Container service (ECS).
This executor plugin is well suited for low to medium compute intensive electrons with modest memory requirements. Since the AWS ECS,
services offers very quick spin up times, this executor is a good fit for workflows with a large number of independent tasks that can
be dispatched simultaneously.

Since this is a cloud executor, proper IAM credentials, permissions and roles must be configured prior to using this executor.
This executor uses different AWS services (S3, ECR and ECS) to successfully run a task. To this end the IAM roles and policies must be
configured so that the executor has the necessary permissions to interact with these.

The following JSON policy document lists the necessary IAM permissions required by the executor

.. code:: json

    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask",
                "ecs:ListTasks",
                "ecs:DescribeTasks"
            ],
            "Resource": "*",
            "Condition": {
                "ArnEquals": {
                    "ecs:cluster": "arn:aws:ecs:us-east-1:348041629502:cluster/covalent-fargate-cluster"
                }
            }
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ecs:RegisterTaskDefinition",
                "ecr:GetAuthorizationToken"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole",
                "ecr:GetDownloadUrlForLayer",
                "s3:ListBucket",
                "ecr:UploadLayerPart",
                "ecr:PutImage",
                "s3:PutObject",
                "s3:GetObject",
                "iam:PassRole",
                "ecr:BatchGetImage",
                "ecr:CompleteLayerUpload",
                "logs:GetLogEvents",
                "ecr:InitiateLayerUpload",
                "ecr:BatchCheckLayerAvailability"
            ],
            "Resource": [
                "arn:aws:ecr:*:348041629502:repository/covalent-fargate-task-images",
                "arn:aws:iam::348041629502:role/CovalentFargateTaskRole",
                "arn:aws:iam::348041629502:role/ecsTaskExecutionRole",
                "arn:aws:logs:*:348041629502:log-group:covalent-fargate-task-logs:log-stream:*",
                "arn:aws:s3:::covalent-fargate-task-resources/*",
                "arn:aws:s3:::covalent-fargate-task-resources"
            ]
        }
    ]
}
