.. _awslambda_executor:

🔌 AWS Lambda Executor
"""""""""""""""""""""""""""

.. image:: AWS_Lambda.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Lambda serverless compute service. It is appropriate
to use this plugin for electrons that are expected to be short lived, low in compute intensity. This plugin can also be used for workflows with a high number of electrons
that are embarassingly parallel aka fully independent of each other.

The AWS resources required by this executor are quite minimal 1) S3 bucket for caching objects 2) Container based AWS lambda function 3) IAM role for  the Lambda.

The following snippet shows the required terraform to spin up the necessary resources and can be used as a base template

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
        function_name = "my-lambda-function"
        s3_bucket_name="covalent-lambda-job-resources",
        execution_role="covalent-lambda-execution-role"
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
    Users may encounter failures with dispatching workflows on MacOS due to errors with importing the `psutil` module. This is a known issue and will be
    addressed in a future sprint.

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
   * - function_name
     - Yes
     - ``-``
     - Name of the AWS lambda function to be used at runtime
   * - s3_bucket_name
     - Yes
     - ``-``
     - Name of an AWS S3 bucket that the executor must use to cache object files
   * - credentials_file
     - No
     - ~/.aws/credentials
     - The path to your AWS credentials file
   * - profile
     - No
     - default
     - AWS profile used for authentication
   * - poll_freq
     - No
     - 5
     - Time interval between successive polls to the lambda function
   * - cache_dir
     - No
     - ~/.cache/covalent
     - Path on the local file system to a cache
   * - timeout
     - No
     - ``900``
     - Duration in seconds to keep polling the task for results/exceptions raised

The following snippet shows how users may modify their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ to provide
the necessary input arguments to the executor:

.. code-block:: bash

    [executors.awslambda]
    function_name = "my-lambda-function"
    s3_bucket_name = "covalent-lambda-job-resources"
    credentials_file = "/home/<user>/.aws/credentials"
    profile = "default"
    region = "us-east-1"
    cache_dir = "/home/<user>/.cache/covalent"
    poll_freq = 5
    timeout = 60

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
        function_name = "my-lambda-function"
        s3_bucket_name="my_s3_bucket",
        credentials_file="my_custom_credentials",
        profile="custom_profile",
        region="us-east-1",
        cache_dir="/home/<user>/covalent/cache",
        poll_freq=5,
        timeout=60
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
   * - AWS Lambda function
     - function_name
     - Name of the AWS lambda function created in AWS

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


where ``<bucket-name>`` is the name of an S3 bucket to be used by the executor to store temporary files generated during task
execution. The lambda function interacts with the S3 bucket as well as with the AWS Cloudwatch service to route any log messages.
Due to this, the lambda function must have the necessary IAM permissions in order to do so. Users must provision an IAM role that has
the ``AWSLambdaExecute`` policy attached to it. The policy document is summarized here for convenience:

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

Users can use the following `Terraform <https://www.terraform.io/>`_ snippet as a starting point to spin up the required resources

.. code-block:: terraform

    provider aws {}

    resource aws_s3_bucket bucket {
        ...
    }

    resource aws_iam_role lambda_iam {
        name = var.aws_lambda_iam_role_name
        assume_role_policy = jsonencode({
            Version = "2012-10-17"
            Statement = [
                {
                    Action = "sts:AssumeRole"
                    Effect = "Allow"
                    Sid    = ""
                    Principal = {
                        Service = "lambda.amazonaws.com"
                }
            },
        ]
        })
        managed_policy_arns = [ "arn:aws:iam::aws:policy/AWSLambdaExecute" ]
    }

    resource aws_lambda_function lambda {
        function_name = "my-lambda-function"
        role = aws_iam_role.lambda_iam.arn
        packge_type = "Image"
        timeout = <timeout value in seconds, max 900 (15 minutes), defaults to 3>
        memory_size = <Max memory in MB that the Lambda is expected to use, defaults to 128>
        image_uri = <URI to the container image used by the lambda, defaults to `public.ecr.aws/covalent/covalent-lambda-executor:stable`>
    }

For more information on how to create IAM roles and attach policies in AWS, refer to `IAM roles <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html>`_.
For more information on AWS S3, refer to `AWS S3 <https://aws.amazon.com/s3/>`_.
