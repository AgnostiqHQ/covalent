.. _awslambda_executor:

🔌 AWS Lambda Executor
"""""""""""""""""""""""""""

.. image:: AWS_Lambda.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Lambda serverless compute service. It is appropriate
to use this plugin for electrons that are expected to be short lived and low in compute intensity. This plugin can also be used
for workflows with several short lived embarassingly parallel tasks aka horizontal workflows.


1. Installation
###############
To use this plugin with Covalent, simply install it using `pip`:

.. code-block:: shell

    pip install covalent-awslambda-plugin

.. note::
    Due to the isolated nature of AWS Lambda, the packages available on that environment are limited. This means that only the modules that
    come with python out-of-the-box are accessible to your function. `Deps` are also limited in a similar fashion. However, AWS does provide
    a workaround for pip package installations: https://aws.amazon.com/premiumsupport/knowledge-center/lambda-python-package-compatible/.


2. Usage Example
################

This is an example of how a workflow can be constructed to use the AWS Lambda executor. In the example, we join two words to form a phrase
and return an excited phrase.

.. code-block:: python

    import covalent as ct
    from covalent.executor import AWSLambdaExecutor

    executor = AWSLambdaExecutor(
        region="us-east-1",
        lambda_role_name="CovalentLambdaExecutionRole",
        s3_bucket_name="covalent-lambda-job-resources",
        timeout=60,
        memory_size=512
        )

    @ct.electron(executor=executor)
    def join_words(a, b):
        return ",".join([a, b])

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

.. code-block:: bash

    Hello, World!

In order for the above workflow to run successfully, one has to provision the required AWS resources as mentioned in :ref:`required_aws_resources`.

.. note::
    Users may encounter failures with dispatching workflows on MacOS due to errors with importing the `psutil` module. This is a known issue and will be       addressed in a future sprint.

3. Overview of configuration
############################

The following table shows a list of all input arguments including the required arguments to be supplied when instantiating the executor:

.. list-table:: Title
   :widths: 25 25 25 50
   :header-rows: 1

   * - Config Value
     - Is Required
     - Default
     - Description
   * - credentials_file
     - No
     - ~/.aws/credentials
     - The path to your AWS credentials file
   * - profile
     - No
     - default
     - AWS profile used for authentication
   * - region
     - Yes
     - us-east-1
     - AWS region to use for client calls
   * - lambda_role_name
     - Yes
     - CovalentLambdaExecutionRole
     - The IAM role this lambda will assume during execution of your tasks
   * - s3_bucket_name
     - Yes
     - covalent-lambda-job-resources
     - Name of an AWS S3 bucket that the executor can use to store temporary files
   * - timeout
     - Yes
     - 60
     - Duration in seconds before the lambda times out
   * - memory_size
     - Yes
     - 512
     - Amount in MB of memory to allocate to the lambda
   * - poll_freq
     - No
     - 5
     - Time interval between successive polls to the lambda function
   * - cache_dir
     - No
     - ~/.cache/covalent
     - Path on the local file system to a cache
   * - cleanup
     - No
     - True
     - Flag represents whether or not to cleanup temporary files generated during execution

The following snippet shows how users may modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ to provide
the necessary input arguments to the executor:

.. code-block:: bash

    [executors.awslambda]
    credentials_file = "/home/<user>/.aws/credentials"
    profile = "default"
    region = "us-east-1"
    lambda_role_name = "CovalentLambdaExecutionRole"
    s3_bucket_name = "covalent-lambda-job-resources"
    cache_dir = "/home/<user>/.cache/covalent"
    poll_freq = 5
    timeout = 60
    memory_size = 512
    cleanup = true

Within a workflow, users can use this executor with the default values configured in the configuration file as follows:

.. code-block:: python

    import covalent as ct

    @ct.electron(executor="awslambda")
    def task(x, y):
        return x + y


Alternatively, users can customize this executor entirely by providing their own values to its constructor as follows:

.. code-block:: python

    import covalent as ct
    from covalent.executor import AWSLambdaExecutor

    lambda_executor = AWSLambdaExecutor(
        credentials_file="my_custom_credentials",
        profile="custom_profile",
        region="us-east-1",
        lambda_role_name="my_lambda_role_name",
        s3_bucket_name="my_s3_bucket",
        cache_dir="/home/<user>/covalent/cache",
        poll_freq=5,
        timeout=30,
        memory_size=512,
        cleanup=True
        )

    @ct.electron(executor=lambda_executor)
    def task(x, y):
        return x + y

.. _required_aws_resources:

4. Required AWS Resources
###########################

In order for the executor to work end-to-end, the following resources need to be configured
either with `Terraform <https://www.terraform.io/>`_ or manually provisioned on the `AWS Dashboard <https://aws.amazon.com/>`_:

.. list-table:: Title
   :widths: 25 25 50
   :header-rows: 1

   * - Resource
     - Config Name
     - Description
   * - IAM Role
     - lambda_role_name
     - The IAM role this lambda will assume during execution of your tasks
   * - S3 Bucket
     - s3_bucket_name
     - Name of an AWS S3 bucket that the executor can use to store temporary files

The following JSON policy document shows the necessary IAM permissions required for the executor
to properly run tasks using the AWS Lambda compute service:

.. dropdown:: IAM Policy

    .. code-block:: json

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


where `<bucket-name>` is the name of an S3 bucket to be used by the executor to store temporary files generated during task
execution. By default, the Lambda executor looks for an S3 bucket with the name `covalent-lambda-job-resources` in the user's
AWS account.
The executor creates an AWS Lambda function using a deployment package containing the code to be executed. The created
lambda function interacts with the S3 bucket as well as with the AWS Cloudwatch service to route any log messages.
Due to this, the lambda function must have the necessary IAM permissions in order to do so. By default, the executor assumes that the
user has already provisioned an IAM role named `CovalentLambdaExecutionRole` that has the `AWSLambdaExecute` policy attached to it.
The policy document is summarized here for convenience:

.. dropdown:: Covalent Lambda Execution Role Policy

    .. code-block:: json

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

For more information on how to create IAM roles and attach policies in AWS, refer to `IAM roles <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html>`_.
For more information on AWS S3, refer to `AWS S3 <https://aws.amazon.com/s3/>`_.
