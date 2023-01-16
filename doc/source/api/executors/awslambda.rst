.. _awslambda_executor:

AWS Lambda Executor
"""""""""""""""""""""""""""

.. image:: AWS_Lambda.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Lambda serverless compute service. It is appropriate
to use this plugin for electrons that are expected to be short lived, low in compute intensity. This plugin can also be used for workflows with a high number of electrons
that are embarassingly parallel (fully independent of each other).

The following AWS resources are required by this executor

* Container based `AWS Lambda <https://docs.aws.amazon.com/lambda/latest/dg/welcome.html>`_ function
* `AWS S3 <https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html>`_ bucket for caching objects
* `IAM <https://docs.aws.amazon.com/iam/index.html>`_ role for Lambda
* `ECR <https://docs.aws.amazon.com/ecr/index.html>`_ container registry for storing docker images


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
        s3_bucket_name="covalent-lambda-job-resources"
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

In order for the executor to work end-to-end, the following resources need to be provisioned apriori.

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
   * - AWS Elastic Container Registry (ECR)
     - ``-``
     - The container registry that contains the docker images used by the lambda function to execute tasks

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
        bucket = "my-s3-bucket"
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

    resource aws_ecr_repository lambda_ecr {
        name = "lambda_container_registry"
    }

    resource aws_lambda_function lambda {
        function_name = "my-lambda-function"
        role = aws_iam_role.lambda_iam.arn
        packge_type = "Image"
        timeout = <timeout value in seconds, max 900 (15 minutes), defaults to 3>
        memory_size = <Max memory in MB that the Lambda is expected to use, defaults to 128>
        image_uri = aws_ecr_repository.lambda_ecr.repository_url
    }

For more information on how to create IAM roles and attach policies in AWS, refer to `IAM roles <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create.html>`_.
For more information on AWS S3, refer to `AWS S3 <https://aws.amazon.com/s3/>`_.

.. note::

    The lambda function created requires a docker image to execute the any tasks required by it. We distribute ready to use AWS Lambda executor docker images that user's can pull and push to their private ECR registries before dispatching workflows.

    The base docker image can be obtained as follows

    .. code:: bash

        docker pull public.ecr.aws/covalent/covalent-lambda-executor:stable

    Once the image has been obtained, user's can tag it with their registry information and upload to ECR as follows

    .. code:: bash

        aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
        docker tag public.ecr.aws/covalent/covalent-lambda-executor:stable <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<my-repository>:tag
        docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/<my-repository>:tag


5. Custom Docker images
########################

As mentioned earlier, the AWS Lambda executor uses a ``docker`` image to execute an electron from a workflow. We distribute AWS Lambda executor base docker images that contain just the essential dependencies such as ``covalent`` and ``covalent-aws-plugins``. However if the electron to be executed using the Lambda executor depends on Python packages that are not present in the base image by default, users will have to a build custom images prior to running their Covalent workflows using the AWS Lambda executor. In this section we cover the necessary steps required to extend the base executor image by installing additional Python packages and pushing the **derived** image to a private elastic container registry (ECR)

.. note::

   Using ``PipDeps`` as described in the :doc:`../deps` section with the AWS Lambda executor is currently not supported as it modifies the execution environment of the lambda function at runtime. As per AWS best practices for Lambda it is recommended to ship the lambda function as a self-contained object that has all of its dependencies in a ``deployment`` package/container image as described in detail `here <https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-package.html>`_

All of our base AWS executor images are available in the AWS public registries and can be downloaded locally for consumption as described here `here <https://docs.aws.amazon.com/AmazonECR/latest/public/docker-pull-ecr-image.html>`_. For instance the ``stable`` AWS Lambda executor image can be downloaded from public ECR as follows


.. code-block:: bash

   aws ecr-public get-login-password --region <aws-region> | docker login --username AWS --password-stdin publc.ecr.aws
   docker pull public.ecr.aws/covalent/covalent-lambda-executor:stable


.. note::

   Executor images with the ``latest`` tag are also routinely pushed to the same registry. However, we strongly recommended using the **stable** tag when running executing workflows usin the AWS Lambda executor. The ``<aws-region>`` is a placeholder for the actual AWS region to be used by the user


Once the lambda base executor image has been downloaded, users can build upon that image by installing all the Python packages required by their tasks. The base executor uses a build time argument named ``LAMBDA_TASK_ROOT`` to set the install path of all python packages to ``/var/task`` inside the image. When extending the base image by installing additional python packages, it is **recommended** to install them to the same location so that they get resolved properly during runtime. Following is a simple example of how users can extend the AWS lambda base image by creating their own ``Dockerfile`` and installting additional packages such as ``numpy``, ``pandas`` and ``scipy``.


.. code-block:: docker

   # Dockerfile

   FROM public.ecr.aws/covalent/covalent-lambda-executor:stable as base

   ARG LAMBDA_TASK_ROOT=/var/task

   RUN pip install --target ${LAMBDA_TASK_ROOT} numpy pandas scipy


.. warning::

   Do **not** override the entrypoint of the base image in the derived image when installing new packages. The docker  ``ENTRYPOINT`` of the base image is what that gets trigged when AWS invokes your lambda function to execute the workflow electron


Once the ``Dockerfile`` has been created the derived image can be built as follows

.. code-block:: bash

   docker build -f Dockerfile -t my-custom-lambda-executor:latest



Pushing to ECR
^^^^^^^^^^^^^^^^^^^^^

After a successful build of the derived image, it needs to be uploaded to ECR so that it can be consumed by a lambda function when triggered by Covalent. As as first step, it is required to create an elastic container registry to hold the dervied executor images. This can be easily done by using the AWS CLI tool as follows

.. code-block:: bash

   aws ecr create-repository --repository-name covalent/my-custom-lambda-executor


To upload the derived image to this registry, we would need to tag our local image as per the AWS guide and push the image to the registry as described `here <https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html>`_. To push an image, first one needs to authenticate with AWS and login their docker client

.. code-block:: bash

   aws ecr get-login-password --region <aws-region> | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.region.amazonaws.com

Once the login is successful, the local image needs to be re-tagged with the ECR repository information. If the image tag is omitted, ``latest`` is applied by default. In the following code block we show how to tag the derived image ``my-custom-lambda-executor:latest`` with the ECR information so that it can be uploaded successfully

.. code-block:: bash

   docker tag my-custom-lambda-executor:latest <aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/my-custom-lambda-executor:latest


.. note::

   <aws-account-id> and <aws-region> are placeholders for the actual AWS account ID and region to be used by the users



Deploying AWS Lambda function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the derived image has been built and pushed to ECR, users need to create a Lambda function or update an existing one to use the new derived image instead of the base image executor image at runtime. A new AWS Lambda function can be quite easily created using the AWS Lambda CLI ``create-function`` command as follows

.. code-block:: bash

   aws lambda create-function --function-name "my-covalent-lambda-function" --region <aws-region> \
        --package-type Image \
        --code ImageUri=<aws-account-id>.dkr.ecr.<aws-region>.amazonaws.com/my-custom-lambda-executor:latest \
        --role <Lambda executor role ARN> \
        --memory-size 512 \
        --timeout 900

The above CLI command will register a new AWS lambda function that will use the user's custom derived image ``my-custom-lambda-executor:latest`` with a memory size of  ``512 MB`` and a timeout values of ``900`` seconds. The ``role`` argument is used to specify the ARN of the IAM role the AWS Lambda can assume during execution. The necessary permissions for the IAM role have been provided in ``Required AWS resources`` section. More details about creating and updating AWS lambda functions can be found `here <https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-images.html>`_.
