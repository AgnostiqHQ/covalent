.. _aws_plugins:

🔌 AWS Plugins
"""""""""""""""""""""""""""

.. image:: AWS_Plugins.png


`Covalent <https://github.com/AgnostiqHQ/covalent>`_  is a python based workflow orchestration tool used to execute HPC and quantum tasks in heterogenous environments.

By installing Covalent AWS Plugins users can leverage a broad plugin ecosystem to execute tasks using AWS resources best fit for each task.


.. .. raw:: html

..     <div style="text-align: left; margin-top: 2rem">
..         <img style="display: inline-block" src="./../../_images/covalent-ec2-code-example.png"/>
..     </div>




.. panels::
    :container: container-lg pb-0
    :column: col-lg-5 p-0 mt-3 mb-2
    :body: none

    Covalent AWS Plugins installs a set of executor plugins that allow tasks to be run in an EC2 instance, AWS Lambda, AWS ECS Cluster, AWS Batch Compute Environment, and as an AWS Braket Job for tasks requiring Quantum devices.
    ---
    :column: col-lg-7 p-0 mt-3 mb-2

    .. image:: covalent-ec2-code-example.png

..


If you're new to covalent visit our :doc:`Getting Started Guide. <../../getting_started/index>`

===========================================
1. Installation
===========================================

To use the AWS plugin ecosystem with Covalent, simply install it with :code:`pip`:

.. code:: bash

   pip install "covalent-aws-plugins[all]""

This will ensure that all the AWS executor plugins listed below are installed.


.. note::

   Users may require `Docker <https://docs.docker.com/get-docker/>`_ and `Terraform <https://www.terraform.io/downloads>`_ to be installed to use the Braket & EC2 plugins respectively.


===========================================
2. Included Plugins
===========================================

While each plugin can be seperately installed installing the above pip package installs all of the below plugins.


.. list-table::
   :widths: 1 2 3
   :header-rows: 1

   * -
     - Plugin Name
     - Use Case
   * -
        .. image:: ./Batch.png
            :width: 48
            :align: center
     - AWS Batch Executor
     - **Useful for heavy compute workloads (high CPU/memory).** Tasks are queued to execute in the user defined Batch compute environment.
   * -
        .. image:: ./EC2.png
            :width: 48
            :align: center
     - AWS EC2 Executor
     - **General purpose compute workloads where users can select compute resources.** An EC2 instance is auto-provisioned using terraform with selected compute settings to execute tasks.
   * -
        .. image:: ./Braket.png
            :width: 48
            :align: center
     - AWS Braket Executor
     - **Suitable for Quantum/Classical hybrid workflows.** Tasks are executed using a combination of classical and quantum devices.
   * -
        .. image:: ./ECS.png
            :width: 48
            :align: center
     - AWS ECS Executor
     - **Useful for moderate to heavy workloads (low memory requirements).** Tasks are executed in an AWS ECS cluster as containers.
   * -
        .. image:: ./Lambda.png
            :width: 48
            :align: center
     - AWS Lambda Executor
     - **Suitable for short lived tasks that can be parallalized (low memory requirements).** Tasks are executed in serverless AWS Lambda functions.


===========================================
3. Usage Example
===========================================

- Firstly, import covalent

.. code-block:: python

    import covalent as ct

- Secondly, define your executor

.. tabbed:: Batch

    .. code-block:: python

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

.. tabbed:: EC2
    :selected:

    .. code-block:: python

        executor = ct.executor.EC2Executor(
            instance_type="t2.micro",
            volume_size=8, #GiB
            ssh_key_file="~/.ssh/ec2_key"
        )

.. tabbed:: Braket
    :selected:

    .. code-block:: python

        executor = ct.executor.BraketExecutor(
            s3_bucket_name="braket_s3_bucket",
            ecr_repo_name="braket_ecr_repo",
            braket_job_execution_role_name="covalent-braket-iam-role",
            quantum_device="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
            classical_device="ml.m5.large",
            storage=30,
        )

.. tabbed:: ECS
    :selected:

    .. code-block:: python

        executor = ct.executor.ECSExecutor(
            s3_bucket_name="covalent-fargate-task-resources",
            ecr_repo_name="covalent-fargate-task-images",
            ecs_cluster_name="covalent-fargate-cluster",
            ecs_task_family_name="covalent-fargate-tasks",
            ecs_task_execution_role_name="ecsTaskExecutionRole",
            ecs_task_role_name="CovalentFargateTaskRole",
            ecs_task_subnet_id="subnet-000000e0",
            ecs_task_security_group_id="sg-0000000a",
            ecs_task_log_group_name="covalent-fargate-task-logs",
            vcpu=1,
            memory=2
        )

.. tabbed:: Lambda
    :selected:

    .. code-block:: python

        executor = ct.executor.AWSLambdaExecutor(
            lambda_role_name="CovalentLambdaExecutionRole",
            s3_bucket_name="covalent-lambda-job-resources",
            timeout=60,
            memory_size=512
        )

- Lastly, define a workflow to execute a particular task using one of the above executors

.. code-block:: python

    @ct.electron(
        executor=executor
    )
    def compute_pi(n):
        # Leibniz formula for π
        return 4 * sum(1.0/(2*i + 1)*(-1)**i for i in range(n))

    @ct.lattice
    def workflow(n):
        return compute_pi(n)


    dispatch_id = ct.dispatch(workflow)(100000000)
    result = ct.get_result(dispatch_id=dispatch_id, wait=True)
    print(result.result)

Which should output

.. code-block:: python

    3.141592643589326
