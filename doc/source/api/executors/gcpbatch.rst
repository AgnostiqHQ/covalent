.. _gcpbatch_executor:

🔌 Google Batch Executor
""""""""""""""""""""""""

.. image:: Azure_Batch.png

Covalent Google Batch executor is an interface between Covalent and `Google Cloud Platform's Batch compute service <https://cloud.google.com/batch/docs/get-started>`_. This executor allows execution of Covalent tasks on Google Batch compute service.

This batch executor is well suited for tasks with high compute/memory requirements. The compute resources required can be very easily configured/specified in the executor's configuration. Google Batch scales really well thus allowing users to queue and execute multiple tasks concurrently on their resources efficiently. Google's Batch job scheduler manages the complexity of allocating the resources needed by the task and de-allocating them once the job has finished.


===============
1. Installation
===============

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

    pip install covalent-gpcbatch-plugin


===========================================
2. Usage Example
===========================================

Here we present an example on how a user can use the GCP Batch executor plugin in their Covalent workflows. In this example we train a simple SVM (support vector machine) model using the Google Batch executor. This executor is quite minimal in terms of the required cloud resoures that need to be provisioned prior to first use. The Google Batch executor needs the following cloud resources pre-configured

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

   Details about Google services accounts and how to use them properly can be found `here <https://cloud.google.com/iam/docs/service-account-overview>`_


.. code-block:: python

    from numpy.random import permutation
    from sklearn import svm, datasets
    import covalent as ct

    deps_pip = ct.DepsPip(
      packages=["numpy==1.23.2", "scikit-learn==1.1.2"]
    )

    executor = ct.executor.GCPBatchExecutor(
        bucket_name = "my-gcp-bucket",
        project_id = "my-gcp-project-id",
        container_image_uri = "my-executor-container-image-uri",
        service_account_email = "my-service-account-email",
        vcpu = 2, # Number of vCPUs to allocate
        memory = 512, # Memory in MB to allocate
        time_limit = 300, # Time limit of job in seconds
        poll_freq = 3 # Number of seconds to pause before polling for the job's status
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
