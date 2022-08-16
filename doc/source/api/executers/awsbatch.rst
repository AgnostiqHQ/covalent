.. _awsbatch_executor:

🔌 AWS Batch Executor
"""""""""""""""""""""""""""

.. image:: AWS_Batch.jpg

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Batch compute service.
This executor plugin is well suited for compute/memory intensive tasks such as training machine learning models,
hyperparameter optimization, deep learning etc. With this executor, the compute backend is the Amazon EC2 service,
with instances optimized for compute and memory intensive operations.

This executor plugin can be installed via pip as follows

.. code:: bash

    pip install covalent-awsbatch-plugin==0.9.0rc0

Since this is a cloud executor, proper IAM credentials, permissions and roles must be configured prior to using this executor.
This executor uses different AWS services (S3, ECR and Batch) to successfully run a task. To this end the IAM roles and policies must be
configured so that the executor has the necessary permissions to interact with these.

The following JSON policy document lists the necessary IAM permissions required by the executor

.. dropdown:: AWS Batch IAM policy

    .. code:: json

        {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BatchJobMgmt",
                "Effect": "Allow",
                "Action": [
                    "batch:TerminateJob",
                    "batch:DescribeJobs",
                    "batch:SubmitJob",
                    "batch:RegisterJobDefinition"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ECRAuth",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ECRUpload",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:InitiateLayerUpload",
                    "ecr:UploadLayerPart",
                    "ecr:CompleteLayerUpload",
                    "ecr:PutImage"
                ],
                "Resource": [
                    "arn:aws:ecr:<region>:<account>:repository/<ecr_repo_name>"
                ]
            },
            {
                "Sid": "IAMRoles",
                "Effect": "Allow",
                "Action": [
                    "iam:GetRole",
                    "iam:PassRole"
                ],
                "Resource": [
                    "arn:aws:iam::<account>:role/CovalentBatchJobRole",
                    "arn:aws:iam::<account>:role/ecsTaskExecutionRole"
                ]
            },
            {
                "Sid": "ObjectStore",
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:PutObject",
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::<s3_resource_bucket>/*",
                    "arn:aws:s3:::<s3_resource_bucket>"
                ]
            },
            {
                "Sid": "LogRead",
                "Effect": "Allow",
                "Action": [
                    "logs:GetLogEvents"
                ],
                "Resource": [
                    "arn:aws:logs:<region>:<account>:log-group:<cloudwatch_log_group_name>:log-stream:*"
                ]
            }
        ]
    }


This executor builds a docker image locally on the user's machine with the function to be exected baked inside the image
along with its arguments and keyword arguments. The executor requires that `Docker <https://www.docker.com/>`_ be
properly installed and configured on the user's machine prior to using this executor in workflows. The executor the uploads
the built docker image to the elastic container registry provided by the user. Following this, the executor registers a AWS batch job RegisterJobDefinition
that contains links the the ECR repo hosting the built image. Finally the job is submitted to AWS batch for execution.
The output of the job is stored in the S3 bucket provided by the user and the result is retrived from there post execution.

The following snippet shows how a user might configure their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_
to provide override the default executor values

.. code:: bash

    [executors.awsbatch]
    credentials = "/home/user/.aws/credentials"
    profile = ""
    s3_bucket_name = "covalent-batch-job-resources"
    ecr_repo_name = "covalent-batch-job-images"
    batch_job_definition_name = "covalent-batch-jobs"
    batch_queue = "covalent-batch-queue"
    batch_execution_role_name = "ecsTaskExecutionRole"
    batch_job_role_name = "CovalentBatchJobRole"
    batch_job_log_group_name = "covalent-batch-job-logs"
    vcpu = 2
    memory = 3.75
    num_gpus = 0
    retry_attempts = 3
    time_limit = 300
    cache_dir = "/tmp/covalent"
    poll_freq = 10

In the default configuration, jobs can run on any instance from the EC2 C4 compute family. If GPU instances
are required, other instance families should be configured prior to using the executor.

If the parameters to the executor are set in the configuration file, user can them simply use the executor as follows

.. code:: python

    import covalent as ct

    @ct.electron(executor='awsbatch')
    def task(x, y):
        return x + y

Users can also instantiate the executor in the workflows directly by providing the necessary input arguments
to its constructor

.. code:: python

    import covalent as ct
    from covlent.executor import AWSBatchExecutor

    awsbatch = AWSBatchExecutor(
        vcpu=16,
        memory=16,
        time_limit=600
    )

    @ct.electron(executor=awsbatch)
    def task(x, y):
        return x + y

In this scenario, the parameters which are not set explicity are then read from the configuration file.



.. autoclass:: covalent.executor.AWSBatchExecutor
    :members:
    :inherited-members:
