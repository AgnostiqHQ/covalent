
IBMQ Executor
"""""""""""""

This quantum executor accesses IBM Quantum backends through Pennylane's :code:`"qiskit.ibmq"` `device <https://docs.pennylane.ai/projects/qiskit/en/latest/devices/ibmq.html>`_. :code:`IBMQExecutor` introduces thread-based parallelism for circuit execution on the `"qiskit.ibmq"` device. Note that the more efficient :code:`QiskitExecutor` is recommended over :code:`IBMQExecutor` for production use.

===============
1. Installation
===============

The IBMQ executor is not included with base Covalent. To install it, run

.. code:: console

    pip install covalent[qiskit]

================
2. Usage Example
================

Using `IBMQExecutor` requires specifying an IBM Quantum backend through the :code:`backend` argument. The :code:`ibmqx_token` is required if not specified in the configuration (see next section).

.. code:: python

    import covalent as ct
    import pennylane as qml

    # IBMQ executor that uses "ibmq_qasm_simulator" (default).
    ibmq_qasm = ct.executor.IBMQExecutor()

    # IBMQ executor that uses the "ibmq_lima" QPU.
    ibmq_lima = ct.executor.IBMQExecutor(
        backend="ibmq_lima",
        ibmqx_token="<token>",
    )

    @ct.qelectron(executors=[ibmq_qasm, ibmq_lima])
    @qml.qnode(qml.device("default.qubit", wires=2, shots=1024), interface="jax")
    def circuit(x):
        qml.IQPEmbedding(features=x, wires=[0, 1])
        qml.Hadamard(wires=1)
        return qml.probs(wires=range(2))

As a QElectron, the circuit can be called either normally or asynchronously using :code:`circuit.run_later()`. With the default :code:`"cyclic"` selector, circuit calls will `alternate` between the executors, :code:`[ibmq_qasm, ibmq_lima]`.

A synchronous example is shown below.

.. code:: python

    >>> print(circuit([0.5, 0.1]))  # ibmq_qasm_simulator

    DeviceArray([0.51660156, 0.00097656, 0.4814453 , 0.00097656], dtype=float32)

    >>> print(circuit([0.5, 0.1]))  # ibmq_lima

    DeviceArray([0.5048828 , 0.00195312, 0.49316406, 0.        ], dtype=float32)

    >>> print(circuit([0.5, 0.1]))  # ibmq_qasm_simulator (again)

    DeviceArray([0.5097656 , 0.00292969, 0.4873047 , 0.        ], dtype=float32)

Doing this asynchronously:

.. code:: python

    >>> x = [0.6, -1.57]

    >>> # Queue jobs for all three circuit calls simultaneously on IBM Quantum.
    >>> # Uses same executor order as above (qasm, lima, qasm, ...).
    >>> futs = [circuit.run_later(x) for _ in range(3)]

    >>> # Wait for all circuits to finish.
    >>> [fut.result() for fut in futs]

    [DeviceArray([0.51660156, 0.00097656, 0.4814453 , 0.00097656], dtype=float32),
     DeviceArray([0.5048828 , 0.00195312, 0.49316406, 0.        ], dtype=float32),
     DeviceArray([0.5097656 , 0.00292969, 0.4873047 , 0.        ], dtype=float32)]

============================
3. Overview of Configuration
============================

The :code:`IBMQExecutor` configuration is found under :code:`[qelectron.IBMQExecutor]` in the `Covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_.

.. list-table::
    :widths: 2 1 2 3
    :header-rows: 1

    * - Config Key
      - Is Required
      - Default
      - Description
    * - backend
      - Yes
      - ibm_qasm_simulator
      - The name of an IBM Quantum system or simulator.
    * - ibmqx_token
      - Yes/No
      -
      - An access token obtained from IBM Quantum. Required for non-local execution.
    * - hub
      - No
      - ibm-q
      - Hub name for IBM Quantum.
    * - group
      - No
      - open
      - Group name for IBM Quantum.
    * - project
      - No
      - main
      - Project name for IBM Quantum.

===========================
4. Required Cloud Resources
===========================

Users must acquire an access token from the `IBM Quantum Experience <https://quantum-computing.ibm.com/>`_ in order to use IBM systems and simulators.

-----

.. autopydantic_model:: covalent.executor.IBMQExecutor
