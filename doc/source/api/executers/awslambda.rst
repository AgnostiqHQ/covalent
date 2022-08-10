.. _awslambda_executor:

🔌 AWS Lambda Executor
"""""""""""""""""""""""""""

With this executor, users can execute tasks (electrons) or entire lattices using the AWS Lambda serverless compute service. It is appropriate
to use this plugin for electrons that are expected to be short lived and low in compute intensity. This plugin can also be used
for workflows with several short lived embarassingly parallel tasks aka. horizontal workflows.

To use this plugin with Covalent, simply install it using `pip`:

.. code:: shell
    pip install covalent-awslambda-plugin


.. autoclass:: covalent.executor.AWSLambdaExecutor
    :members:
    :inherited-members:
