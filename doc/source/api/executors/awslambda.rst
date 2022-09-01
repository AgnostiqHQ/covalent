.. _awslambda_executor:

🔌 AWS Lambda Executor
"""""""""""""""""""""""""""

.. image:: AWS_Lambda.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Lambda serverless compute service. It is appropriate
to use this plugin for electrons that are expected to be short lived and low in compute intensity. This plugin can also be used
for workflows with several short lived embarassingly parallel tasks aka. horizontal workflows.

.. note::
    Due to the isolated nature of AWS Lambda, the packages available on that environment are limited. This means that only the modules that
    come with python out-of-the-box are accessible to your function. Similarly, not all `Deps` are supported either.

To use this plugin with Covalent, simply install it using `pip`:

.. code:: shell

    pip install covalent-awslambda-plugin

Since this is a cloud executor, proper IAM credentials, permissions and roles must be configured prior to using this executor. This executor
uses the S3 and the AWS lambda service to execute tasks thus the IAM roles and policies must be configured so that
the executor has permissions to interact with the two. The following JSON policy document shows the necessary IAM
permissions required for the executor to properly run tasks using the AWS Lambda compute service

.. dropdown:: IAM Policy

    .. code:: json

        {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:*",
                    "s3-object-lambda:*"
                ],
                "Resource": [
                    "arn:aws:s3:::<bucket-name>",
                    "arn:aws:s3:::<bucket-name>/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "cloudformation:DescribeStacks",
                    "cloudformation:ListStackResources",
                    "cloudwatch:ListMetrics",
                    "cloudwatch:GetMetricData",
                    "ec2:DescribeSecurityGroups",
                    "ec2:DescribeSubnets",
                    "ec2:DescribeVpcs",
                    "kms:ListAliases",
                    "iam:GetPolicy",
                    "iam:GetPolicyVersion",
                    "iam:GetRole",
                    "iam:GetRolePolicy",
                    "iam:ListAttachedRolePolicies",
                    "iam:ListRolePolicies",
                    "iam:ListRoles",
                    "lambda:*",
                    "logs:DescribeLogGroups",
                    "states:DescribeStateMachine",
                    "states:ListStateMachines",
                    "tag:GetResources",
                    "xray:GetTraceSummaries",
                    "xray:BatchGetTraces"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "iam:PassedToService": "lambda.amazonaws.com"
                    }
                }
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:DescribeLogStreams",
                    "logs:GetLogEvents",
                    "logs:FilterLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/*"
            }
        ]
        }


where `<bucket-name>` is the name of S3 bucket to be used by the executor to store temporary files generated during task
execution. By default the Lambda executor looks for an S3 bucket with the name `covalent-lambda-job-resources` in the user's
AWS account.

The executor creates an AWS Lambda function using a deployment package containing the code to be executed. The created
lambda function interacts with the S3 bucket as well with the AWS cloudwatch service to route any log messages. Due to this,
the lambda function must have the necessary IAM permissions in order to do so. By default, the executor assumes that the
user has already provisioned a IAM role named `CovalentLambdaExecutionRole` that has the `AWSLambdaExecute` policy attached to it.
The policy document is summarized here for convenience

.. dropdown:: Covalent Lambda Execution Role Policy

    .. code:: json

        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:*"
                    ],
                    "Resource": "arn:aws:logs:*:*:*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    "Resource": "arn:aws:s3:::*"
                }
            ]
        }



The following snippet shows how users may modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ to provide
the necessary input arguments to the `AWSLambdaExecutor`

.. code:: bash

    [executors.awslambda]
    credentials = "/home/<user>/.aws/credentials"
    profile = "default"
    region = "us-east-1"
    lambda_role_name = "CovalentLambdaExecutionRole"
    s3_bucket_name = "covalent-lambda-job-resources"
    cache_dir = "/home/<user>/.cache/covalent"
    poll_freq = 5
    timeout = 60
    memory_size = 512
    cleanup = true

Within a workflow, users can use this executor with the default values configured in the configuration file as follows

.. code:: python

    import covalent as ct

    @ct.electron(executor="awslambda")
    def task(x, y):
        return x + y


Alternatively, users can customize this executor entirely by providing their own values to its constructor as follows

.. code:: python

    import covalent as ct
    from covalent.executor import AWSLambdaExecutor

    lambda_executor = AWSLambdaExecutor(credentials="my_custom_credentials",
                                profile="custom_profile",
                                region="us-east-1",
                                lambda_role_name="my_lambda_rolen_name",
                                s3_bucket_name="my_s3_bucket",
                                cache_dir="/home/<user>/covalent/cache",
                                poll_freq=5,
                                timeout=30,
                                memory_size=512,
                                cleanup=True)


    @ct.electron(executor=lambda_executor)
    def task(x, y):
        return x + y




.. autoclass:: covalent.executor.AWSLambdaExecutor
    :members:
    :inherited-members:
