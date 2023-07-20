.. _gcpbatch_executor:

Google Batch Executor
""""""""""""""""""""""""

.. image:: GCP_Batch.png

Covalent Google Batch executor is an interface between Covalent and `Google Cloud Platform's Batch compute service <https://cloud.google.com/batch/docs/get-started>`_. This executor allows execution of Covalent tasks on Google Batch compute service.

This batch executor is well suited for tasks with high compute/memory requirements. The compute resources required can be very easily configured/specified in the executor's configuration. Google Batch scales really well thus allowing users to queue and execute multiple tasks concurrently on their resources efficiently. Google's Batch job scheduler manages the complexity of allocating the resources needed by the task and de-allocating them once the job has finished.


===============
1. Installation
===============

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

    pip install covalent-gcpbatch-plugin


===========================================
2. Usage Example
===========================================

Here we present an example on how a user can use the GCP Batch executor plugin in their Covalent workflows. In this example we train a simple SVM (support vector machine) model using the Google Batch executor. This executor is quite minimal in terms of the required cloud resources that need to be provisioned prior to first use. The Google Batch executor needs the following cloud resources pre-configured:

* A Google storage bucket
* Cloud artifact registry for Docker images
* A service account with the following permissions
   * ``roles/batch.agentReporter``
   * ``roles/logging.logWriter``
   * ``roles/logging.viewer``
   * ``roles/artifactregistry.reader``
   * ``roles/storage.objectCreator``
   * ``roles/storage.objectViewer``

.. note::

   Details about Google services accounts and how to use them properly can be found `here <https://cloud.google.com/iam/docs/service-account-overview>`_.


.. code-block:: python

    from numpy.random import permutation
    from sklearn import svm, datasets
    import covalent as ct

    deps_pip = ct.DepsPip(
      packages=["numpy==1.23.2", "scikit-learn==1.1.2"]
    )

    executor = ct.executor.GCPBatchExecutor(
        bucket_name = "my-gcp-bucket",
        region='us-east1',
        project_id = "my-gcp-project-id",
        container_image_uri = "my-executor-container-image-uri",
        service_account_email = "my-service-account-email",
        vcpus = 2,  # Number of vCPUs to allocate
        memory = 512,  # Memory in MB to allocate
        time_limit = 300,  # Time limit of job in seconds
        poll_freq = 3  # Number of seconds to pause before polling for the job's status
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

During the execution of the workflow the user can navigate to the web-based browser UI to see the status of the computations.


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
   * - project_id
     - yes
     - None
     - Google cloud project ID
   * - region
     - No
     - us-east1
     - Google cloud region to use to for submitting batch jobs
   * - bucket_name
     - Yes
     - None
     - Name of the Google storage bucket to use for storing temporary objects
   * - container_image_uri
     - Yes
     - None
     - GCP Batch executor base docker image uri
   * - service_account_email
     - Yes
     - None
     - Google service account email address that is to be used by the batch job when interacting with the resources
   * - vcpus
     - No
     - 2
     - Number of vCPUs needed for the task.
   * - memory
     - No
     - 256
     - Memory (in MB) needed by the task.
   * - retries
     - No
     - 3
     - Number of times a job is retried if it fails.
   * - time_limit
     - No
     - 300
     - Time limit (in seconds) after which jobs are killed.
   * - poll_freq
     - No
     - 5
     - Frequency (in seconds) with which to poll a submitted task.
   * - cache_dir
     - No
     - /tmp/covalent
     - Cache directory used by this executor for temporary files.

This plugin can be configured in one of two ways:

#. Configuration options can be passed in as constructor keys to the executor class :code:`ct.executor.GCPBatchExecutor`

#. By modifying the `covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ under the section :code:`[executors.gcpbatch]`


.. code:: shell

    [executors.gcpbatch]
    bucket_name = <my-gcp-bucket-name>
    project_id = <my-gcp-project-id>
    container_image_uri = <my-base-executor-image-uri>
    service_account_email = <my-service-account-email>
    region = <google region for batch>
    vcpus = 2 # number of vcpus needed by the job
    memory = 256 # memory in MB required by the job
    retries = 3 # number of times to retry the job if it fails
    time_limit = 300 # time limit in seconds after which the job is to be considered failed
    poll_freq = 3 # Frequency in seconds with which to poll the job for the result
    cache_dir = "/tmp" # Path on file system to store temporary objects


===========================================
4. Required Cloud Resources
===========================================

In order to successfully execute tasks using the Google Batch executor, some cloud resources need to be provisioned apriori.

* Google storage bucket

The executor uses a storage bucket to store/cache exception/result objects that get generated during execution.

* Google Docker artifact registry

The executor submits a container job whose image is pulled from the provided ``container_image_uri`` argument of the executor.

* Service account

Keeping good security practices in mind, the jobs are executed using a service account that only has the necessary permissions attached to it that are required for the job to finish.


Users can free to provision these resources as they see fit or they can use Covalent to provision these for them. Covalent CLI can be used to deploy the required cloud resources. Covalent behind the scenes uses `Terraform <https://www.terraform.io/>`_ to provision the cloud resources. The terraform HCL scripts can be found in the plugin's Github repository `here <https://github.com/AgnostiqHQ/covalent-gcpbatch-plugin/tree/develop/covalent_gcpbatch_plugin/assets/infra>`_.

To run the scripts manually, users must first authenticate with Google cloud via their CLI and print out the access tokens with the following commands:

.. code:: shell

  gcloud auth application-default login
  gcloud auth print-access-token


Once the user has authenticated, the infrastructure can be deployed by running the Terraform commands in the ``infra`` folder of the plugin's repository.

.. code:: shell

  terraform plan -out tf.plan
  terrafrom apply tf.plan -var="access_token=<access_token>"

.. note::

  For first time deployment, the terraform provides must be initialized properly via ``terraform init``.

The Terraform script also builds the base executor docker image and uploads it to the artifact registry after getting created. This means that users do not have to manually build and push the image.


.. autoclass:: covalent.executor.GCPBatchExecutor
    :members:
    :inherited-members:
