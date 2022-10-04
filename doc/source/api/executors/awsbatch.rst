.. _awsbatch_executor:

🔌 AWS Batch Executor
"""""""""""""""""""""""""""

.. image:: AWS_Batch.jpg


Covalent is a Pythonic workflow tool used to execute tasks on advanced computing hardware.

This executor plugin interfaces Covalent with `AWS Batch <https://docs.aws.amazon.com/batch/>`_ which allows tasks in a covalent workflow to be executed as AWS batch jobs.

Furthermore, this plugin is well suited for compute/memory intensive tasks such as training machine learning models, hyperparameter optimization, deep learning etc. With this executor, the compute backend is the Amazon EC2 service, with instances optimized for compute and memory intensive operations.


===========================================
1. Installation
===========================================

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

   pip install covalent-awsbatch-plugin


===========================================
2. Usage Example
===========================================

This is an example of how a workflow can be adapted to utilize the AWS Batch Executor. Here we train a simple Support Vector Machine (SVM) model and use an existing AWS Batch Compute environment to run the :code:`train_svm` electron as a batch job. We also note we require :doc:`DepsPip <../../concepts/concepts>` to install the dependencies when creating the batch job.

.. code-block:: python

    from numpy.random import permutation
    from sklearn import svm, datasets
    import covalent as ct

    deps_pip = ct.DepsPip(
      packages=["numpy==1.23.2", "scikit-learn==1.1.2"]
    )

    executor = ct.executor.AWSBatchExecutor(
        s3_bucket_name = "covalent-batch-qa-job-resources",
        batch_job_definition_name = "covalent-batch-qa-job-definition",
        batch_queue = "covalent-batch-qa-queue",
        batch_execution_role_name = "ecsTaskExecutionRole",
        batch_job_role_name = "covalent-batch-qa-job-role",
        batch_job_log_group_name = "covalent-batch-qa-log-group",
        vcpu = 2, # Number of vCPUs to allocate
        memory = 3.75, # Memory in GB to allocate
        time_limit = 300, # Time limit of job in seconds
    )

    # Use executor plugin to train our SVM model.
    @ct.electron(
        executor=executor,
        deps_pip=deps_pip
    )
    def train_svm(data, C, gamma):
        X, y = data
        clf = svm.SVC(C=C, gamma=gamma)
        clf.fit(X[90:], y[90:])
        return clf

    @ct.electron
    def load_data():
        iris = datasets.load_iris()
        perm = permutation(iris.target.size)
        iris.data = iris.data[perm]
        iris.target = iris.target[perm]
        return iris.data, iris.target

    @ct.electron
    def score_svm(data, clf):
        X_test, y_test = data
        return clf.score(
          X_test[:90],
        y_test[:90]
        )

    @ct.lattice
    def run_experiment(C=1.0, gamma=0.7):
        data = load_data()
        clf = train_svm(
          data=data,
          C=C,
          gamma=gamma
        )
        score = score_svm(
          data=data,
        clf=clf
        )
        return score

    # Dispatch the workflow
    dispatch_id = ct.dispatch(run_experiment)(
      C=1.0,
      gamma=0.7
    )

    # Wait for our result and get result value
    result = ct.get_result(dispatch_id=dispatch_id, wait=True).result

    print(result)

During the execution of the workflow one can navigate to the UI to see the status of the workflow, once completed however the above script should also output a value with the score of our model.

.. code-block:: python

    0.8666666666666667

===========================================
3. Overview of Configuration
===========================================

.. list-table::
   :widths: 2 1 2 3
   :header-rows: 1

   * - Config Key
     - Is Required
     - Default
     - Description
   * - profile
     - No
     - default
     - Named AWS profile used for authentication
   * - region
     - Yes
     - us-east-1
     - AWS Region to use to for client calls
   * - credentials
     - No
     - ~/.aws/credentials
     - The path to the AWS credentials file
   * - batch_queue
     - Yes
     - covalent-batch-queue
     - Name of the Batch queue used for job management.
   * - s3_bucket_name
     - Yes
     - covalent-batch-job-resources
     - Name of an S3 bucket where covalent artifacts are stored.
   * - batch_job_definition_name
     - Yes
     - covalent-batch-jobs
     - Name of the Batch job definition for a user, project, or experiment.
   * - batch_execution_role_name
     - No
     - ecsTaskExecutionRole
     - Name of the IAM role used by the Batch ECS agent (the above role should already exist in AWS).
   * - batch_job_role_name
     - Yes
     - CovalentBatchJobRole
     - Name of the IAM role used within the container.
   * - batch_job_log_group_name
     - Yes
     - covalent-batch-job-logs
     - Name of the CloudWatch log group where container logs are stored.
   * - vcpu
     - No
     - 2
     - Number of vCPUs available to a task.
   * - memory
     - No
     - 3.75
     - Memory (in GB) available to a task.
   * - num_gpus
     - No
     - 0
     - Number of GPUs availabel to a task.
   * - retry_attempts
     - No
     - 3
     - Number of times a job is retried if it fails.
   * - time_limit
     - No
     - 300
     - Time limit (in seconds) after which jobs are killed.
   * - poll_freq
     - No
     - 10
     - Frequency (in seconds) with which to poll a submitted task.
   * - cache_dir
     - No
     - /tmp/covalent
     - Cache directory used by this executor for temporary files.

This plugin can be configured in one of two ways:

#. Configuration options can be passed in as constructor keys to the executor class :code:`ct.executor.AWSBatchExecutor`

#. By modifying the `covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ under the section :code:`[executors.awsbatch]`



The following shows an example of how a user might modify their `covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_  to support this plugin:

.. code:: shell

    [executors.awsbatch]
    s3_bucket_name = "covalent-batch-job-resources"
    batch_queue = "covalent-batch-queue"
    batch_job_definition_name = "covalent-batch-jobs"
    batch_execution_role_name = "ecsTaskExecutionRole"
    batch_job_role_name = "CovalentBatchJobRole"
    batch_job_log_group_name = "covalent-batch-job-logs"
    ...


.. autoclass:: covalent.executor.EC2Executor
    :members:
    :inherited-members:


===========================================
4. Required Cloud Resources
===========================================

In order to run your workflows with covalent there are a few notable AWS resources that need to be provisioned first.


.. list-table::
   :widths: 2 1 2 3
   :header-rows: 1

   * - Resource
     - Is Required
     - Config Key
     - Description
   * - AWS S3 Bucket
     - Yes
     - :code:`covalent-batch-job-resources`
     - S3 bucket must be created for covalent to store essential files that are needed during execution.
   * - VPC & Subnet
     - Yes
     - N/A
     - A VPC must be associated with the AWS Batch Compute Environment along with a public or private subnet (there needs to be additional resources created for private subnets)
   * - AWS Batch Compute Environment
     - Yes
     - N/A
     - An AWS Batch compute environment (EC2) that will provision EC2 instances as needed when jobs are submitted to the associated job queue.
   * - AWS Batch Queue
     - Yes
     - :code:`batch_queue`
     - An AWS Batch Job Queue that will queue tasks for execution in it's associated compute environment.
   * - AWS Batch Job Definition
     - Yes
     - :code:`batch_job_definition_name`
     - An AWS Batch job definition that will be replaced by a new batch job definition when the workflow is executed.
   * - AWS IAM Role (Job Role)
     - Yes
     - :code:`batch_job_role_name`
     - The IAM role used within the container.
   * - AWS IAM Role (Execution Role)
     - No
     - :code:`batch_execution_role_name`
     - The IAM role used by the Batch ECS agent (default role ecsTaskExecutionRole should already exist).
   * - Log Group
     - Yes
     - :code:`batch_job_log_group_name`
     - An AWS CloudWatch log group where task logs are stored.



#. To create an AWS S3 Bucket refer to the following `AWS documentation <https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html>`_.
#. To create a VPC & Subnet refer to the following `AWS documentation <https://docs.aws.amazon.com/directoryservice/latest/admin-guide/gsg_create_vpc.html>`_.
#. To create an AWS Batch Queue refer to the following `AWS documentation <https://docs.aws.amazon.com/batch/latest/userguide/create-job-queue.html>`_ it must be a compute environment configured in EC2 mode.
#. To create an AWS Batch Job Definition refer to the following `AWS documentation <https://docs.aws.amazon.com/batch/latest/userguide/create-job-definition-EC2.html>`_ the configuration for this can be trivial as covalent will update the Job Definition prior to execution.
#. To create an AWS IAM Role for batch jobs (Job Role) one can provision a policy with the following permissions (below) then create a new role and attach with the created policy. Refer to the following `AWS documentation <https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_job-functions_create-policies.html>`_ for an example of creating a policy & role in IAM.

.. dropdown:: AWS Batch IAM Job Policy

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


.. ===========================================
.. 5. Source
.. ===========================================

.. autoclass:: covalent.executor.AWSBatchExecutor
    :members:
    :inherited-members:
