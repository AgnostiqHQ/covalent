.. _awsbraket_executor:

🔌 AWS Braket Executor
"""""""""""""""""""""""""""

This executor interfaces Covalent with `AWS Braket Hybrid Jobs <https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs.html/>`_ service by
containerizing tasks using Docker and dispatching them to be executed on AWS Braket. This executor is a suitable choice
for workflow containing tasks that require a mix of classical and quantum compute resources. In order for
workflows to be deployable, users must have AWS credentials allowing access to Braket, S3, ECR, and
some other services. Users will need additional permissions to provision or manage cloud
infrastructure used by this plugin.

Since this is a cloud executor, proper IAM credentials, permissions and roles must be configured prior to using this executor.
This executor uses different AWS services (S3, ECR and Braket) to successfully run a task. To this end the IAM roles and policies must be
configured so that the executor has the necessary permissions to interact with these.

The following IAM policy can be use to properly configure the required IAM role for this executor

.. code:: json

    {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "cloudwatch:PutMetricData",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "cloudwatch:namespace": "/aws/braket"
                }
            }
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": "arn:aws:iam::<account id>:role/CovalentBraketJobsExecutionRole",
            "Condition": {
                "StringLike": {
                    "iam:PassedToService": "braket.amazonaws.com"
                }
            }
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "braket:CreateJob",
                "braket:GetJob",
                "braket:SearchDevices",
                "braket:SearchJobs",
                "braket:CreateQuantumTask",
                "ecr:GetAuthorizationToken",
                "iam:ListRoles",
                "braket:ListTagsForResource",
                "braket:UntagResource",
                "braket:TagResource",
                "braket:GetDevice",
                "braket:GetQuantumTask",
                "braket:CancelQuantumTask",
                "braket:SearchQuantumTasks",
                "braket:CancelJob"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketPublicAccessBlock",
                "logs:DescribeLogStreams",
                "ecr:GetDownloadUrlForLayer",
                "logs:StartQuery",
                "s3:CreateBucket",
                "s3:ListBucket",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
                "s3:PutObject",
                "s3:GetObject",
                "logs:CreateLogStream",
                "logs:GetLogEvents",
                "ecr:BatchGetImage",
                "s3:PutBucketPolicy",
                "ecr:BatchCheckLayerAvailability"
            ],
            "Resource": [
                "arn:aws:s3:::amazon-braket-covalent-job-resources",
                "arn:aws:s3:::amazon-braket-covalent-job-resources/*",
                "arn:aws:logs:*:*:log-group:/aws/braket*",
                "arn:aws:ecr:*:<account id>:repository/covalent-braket-job-images"
            ]
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": "logs:GetQueryResults",
            "Resource": "arn:aws:logs:*:*:log-group:*"
        },
        {
            "Sid": "VisualEditor5",
            "Effect": "Allow",
            "Action": "logs:StopQuery",
            "Resource": "arn:aws:logs:*:*:log-group:/aws/braket*"
        }
    ]
}


This executor uses `Docker <https://www.docker.com/>`_ to build an image containing the function code to be executed on Braket locally
on the user's machine and uploads it to the provided container registry. Following the image update, a ``braket job`` is created
with the image as a template. The job uploads the result to the S3 bucket specified by the user which the executor then
parses to retrive the result object.

This executor plugin can be installed locally via ``pip``

.. code:: bash

    pip install covalent-braket-plugin

Users must add the correct entries to their Covalent `configuration <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ to support the Braket Hybrid Jobs plugin.
Below is an example which works using some basic infrastructure created for testing purposes:

.. code:: bash

    [executors.braket]
    credentials = "/home/user/.aws/credentials"
    profile = ""
    s3_bucket_name = "amazon-braket-covalent-job-resources"
    ecr_repo_name = "covalent-braket-job-images"
    cache_dir = "/tmp/covalent"
    poll_freq = 30
    braket_job_execution_role_name = "CovalentBraketJobsExecutionRole"
    quantum_device = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"
    classical_device = "ml.m5.large"
    storage = 30
    time_limit = 300

Note that the S3 bucket must always start with ``amazon-braket-``
and the set of classical devices is constrained to `certain types <https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs-configure-job-instance-for-script.html/>`_.

Having provided the executor configuration as above, within workflows users can use the executor as follows

.. code:: python

    import covalent as ct

    @ct.electron(executor="braket")
    def my_hybrid_task(num_qubits: int, shots: int):
        import pennylane as qml

        # These are passed to the Hybrid Jobs container at runtime
        device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
        s3_bucket = os.environ["AMZN_BRAKET_OUT_S3_BUCKET"]
        s3_task_dir = os.environ["AMZN_BRAKET_TASK_RESULTS_S3_URI"].split(s3_bucket)[1]

        device = qml.device(
            "braket.aws.qubit",
    	device_arn=device_arn,
    	s3_destination_folder=(s3_bucket, s3_task_dir),
    	wires=num_qubits,
    	shots=shots,
    	parallel=True,
    	max_parallel=4
        )

        @qml.qnode(device)
        def circuit():
            # Define the circuit here

        # Invoke the circuit and iterate as needed

Alternatively, users can also instantiate the executor class explicity with their custom arguments as follows

.. code:: python
    import covalent as ct

    executor = ct.executor.BraketExecutor(
    classical_device = "ml.p3.2xlarge" # Includes a V100 GPU and 8 vCPUs
    quantum_device = "arn:aws:braket:::device/qpu/rigetti/Aspen-11", # 47-qubit QPU
    time_limit = 600, # 10-minute time limit
    )
    ef my_custom_hybrid_task():
        # Task definition goes here

.. autoclass:: covalent.executor.BraketExecutor
    :members:
    :inherited-members:
