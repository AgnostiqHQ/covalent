.. _azurebatch_executor:

🔌 Azure Batch Executor
""""""""""""""""""""""""

.. image:: Azure_Batch.png

Azure Batch Executor plugin is an interface between Covalent and `Microsoft Azure Batch <https://azure.microsoft.com/en-us/products/batch/#overview>`_. It allows execution of Covalent tasks on Azure Batch.

Azure Batch is well suited for compute/memory intensive tasks since the resource pool of compute virtual machines can be scaled accordingly. Furthermore, Azure Batch allows to run tasks in parallel on multiple virtual machines and their scheduling engine manages execution of the tasks.

===============
1. Installation
===============

To use this plugin with Covalent, simply install it using :code:`pip`:

.. code:: bash

    pip install covalent-azurebatch-plugin


================
2. Usage Example
================

In this example, we train a Support Vector Machine (SVM) using an instance of the Azure Batch executor. The :code:`train_svm` electron is submitted as a batch job in an existing Azure Batch Compute environment. Note that we also require :doc:`DepsPip <../../concepts/concepts>`) in order to install the python package dependencies before executing the electron in the batch environment.

.. code-block:: python

    from numpy.random import permutation
    from sklearn import svm, datasets
    import covalent as ct

    from covalent.executor import AzureBatchExecutor

    deps_pip = ct.DepsPip(
        packages=["numpy==1.22.4", "scikit-learn==1.1.2"]
    )

    executor = AzureBatchExecutor(
        tenant_id="tenant-id",
        client_id="client-id",
        client_secret="client-secret",  # pragma: allowlist secret
        batch_account_url="https://covalent.eastus.batch.azure.com",
        batch_account_domain="batch.core.windows.net",
        storage_account_name="covalentbatch",
        storage_account_domain="blob.core.windows.net",
        pool_id="covalent-pool",
        retries=3,
        time_limit=300,
        cache_dir="/tmp/covalent",
        poll_freq=10
    )

    # Use executor plugin to train our SVM model
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
            X_test[:90],y_test[:90]
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

    # Dispatch the workflow.
    dispatch_id = ct.dispatch(run_experiment)(
            C=1.0,
            gamma=0.7
    )

    # Wait for our result and get result value
    result = ct.get_result(dispatch_id, wait=True).result

    print(result)

During the execution of the workflow, one can navigate to the UI to see the status of the workflow. Once completed, the above script should also output a value with the score of our model.

.. code-block:: python

    0.8666666666666667


============================
3. Overview of Configuration
============================

.. list-table::
   :widths: 2 1 2 3
   :header-rows: 1

   * - Config Key
     - Required
     - Default
     - Description
   * - tenant_id
     - Yes
     - None
     - Azure tenant ID
   * - client_id
     - Yes
     - None
     - Azure client ID
   * - client_secret
     - Yes
     - None
     - Azure client secret
   * - batch_account_url
     - Yes
     - None
     - Azure Batch account URL
   * - batch_account_domain
     - No
     - batch.core.windows.net
     - Azure Batch account domain
   * - storage_account_name
     - Yes
     - None
     - Azure Storage account name
   * - storage_account_domain
     - No
     - blob.core.windows.net
     - Azure Storage account domain
   * - pool_id
     - Yes
     - None
     - Azure Batch pool ID
   * - retries
     - No
     - 3
     - Number of retries for Azure Batch job
   * - time_limit
     - No
     - 300
     - Time limit for Azure Batch job
   * - cache_dir
     - No
     - /tmp/covalent
     - Directory to store cached files
   * - poll_freq
     - No
     - 10
     - Polling frequency for Azure Batch job

#. Configuration options can be passed in as constructor keys to the executor class :code:`ct.executor.AzureBatchExecutor`

#. By modifying the `covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_ under the section :code:`[executors.azurebatch]`

The following shows an example of how a user might modify their `covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_  to support this plugin:

.. code:: shell

    [executors.azurebatch]
    tenant_id="tenant-id",
    client_id="client-id",
    client_secret="client-secret",  # pragma: allowlist secret
    batch_account_url="https://covalent.eastus.batch.azure.com",
    batch_account_domain="batch.core.windows.net",
    storage_account_name="covalentbatch",
    storage_account_domain="blob.core.windows.net",
    pool_id="covalent-pool",
    retries=5,
    time_limit=500,
    ...


===========================
4. Required Cloud Resources
===========================

In order to use this plugin, you will need to have the following Azure resources provisioned first.

.. list-table::
   :widths: 2 1 2 3
   :header-rows: 1

   * - Resource
     - Is Required
     - Config Key
     - Description
   * - Batch Account
     - Yes
     -
     -
   * - Storage Account
     - Yes
     -
     -
   * - Resource Group
     - Yes
     -
     -
   * - Container Registry
     - Yes
     -
     -
   * - Virtual Network
     - Yes
     -
     -
