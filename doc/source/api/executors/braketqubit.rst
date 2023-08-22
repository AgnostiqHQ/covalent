
AWS Braket Qubit Executor
"""""""""""""

This quantum executor accesses quantum resources operating under the qubit model as
made available through AWS (:code:`"braket.aws.qubit"`).

It utilizes the Pennylane plugin found `here <https://amazon-braket-pennylane-plugin-python.readthedocs.io/en/latest/>`_.
:code:`BraketQubitExecutor` introduces thread-based parallelism for circuit execution on the :code:`"braket.aws.qubit"` device.

===============
1. Installation
===============

:code:`BraketQubitExecutor` is not included in base Covalent.
To use it, you will need to install the Covalent with:

.. code:: console

    pip install covalent[braket]

and have valid AWS credentials as specified `here <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html>`_.

================
2. Usage Example
================

Using :code:`BraketQubitExecutor` requires specifying an AWS Quantum backend through the :code:`device_arn` argument.

.. code:: python

    # Statevector simulator
    sv1 = ct.executor.BraketQubitExecutor(
        device_arn="arn:aws:braket:::device/quantum-simulator/amazon/sv1",
        shots=1024,
        s3_destination_folder=(),
    )
    # Tensor network simulator
    tn1 = ct.executor.BraketQubitExecutor(
        device_arn="arn:aws:braket:::device/quantum-simulator/amazon/tn1",
        shots=1024,
        s3_destination_folder=(),
    )

    @ct.qelectron(executors=[sv1, tn1])
    @qml.qnode(qml.device("default.qubit", wires=2, shots=1000))
    def circuit(x):
        qml.IQPEmbedding(features=x, wires=[0, 1])
        qml.Hadamard(wires=1)
        return [qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))]

As a QElectron, the circuit can be called either normally or asynchronously using :code:`circuit.run_later()`. With the default :code:`"cyclic"` selector, circuit calls will `alternate` between the executors, :code:`[sv1, tn1]`.

Synchronous example output is below

.. code:: python

    >>> print(circuit([0.5, 0.1]))  # alternate between sv1 and tn1

    [array(0.008), array(0.996)]


and asynchronously:

.. code:: python

    >>> x = [0.6, -1.57]

    >>> # Queue jobs for all three circuit calls simultaneously on AWS Braket.
    >>> # Uses same executor order as above (sv1, tn1, ...).
    >>> futs = [circuit.run_later(x) for _ in range(3)]

    >>> # Wait for all circuits to finish.
    >>> [fut.result() for fut in futs]

    [[array(-0.02), array(0.01)],
     [array(0.014), array(-0.022)],
     [array(-0.074), array(0.05)]]

============================
3. Overview of Configuration
============================

The :code:`BraketQubitExecutor` configuration is found under :code:`[qelectron.BraketQubitExecutor]` in the `Covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_.

.. list-table::
    :widths: 2 1 2 3
    :header-rows: 1

    * - Config Key
      - Is Required
      - Default
      - Description
    * - device_arn
      - Yes
      - "" (blank string)
      - A unique identifier used to represent and reference AWS resources. Stands for "Amazon Resource Name".
    * - poll_timeout_seconds
      - No
      - 432000
      - Number of seconds before a poll to remote device is considered timed-out.
    * - poll_interval_seconds
      - No
      - 1
      - Number of seconds between polling of a remote device's status.
    * - max_connections
      - No
      - 100
      - the maximum number of connections in the :code:`Boto3` connection pool.
    * - max_retries
      - No
      - 3
      - The maximum number of times a job will be re-sent if it failed.
===========================
4. Required Cloud Resources
===========================

Users must acquire AWS credentials and make them discoverable following the instructions `here <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html>`_.

-----

.. autopydantic_model:: covalent.executor.BraketQubitExecutor
