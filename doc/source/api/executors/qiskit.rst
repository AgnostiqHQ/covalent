Qiskit Runtime Executor
"""""""""""""""""""""""

This quantum executor provides efficient access to IBM Quantum backends by using runtime sessions for submitting jobs. :code:`QiskitExecutor` uses asyncio for scalable parallelization.

===============
1. Installation
===============

The Qiskit Runtime executor is not included with base Covalent. To install it, run

.. code:: console

    pip install covalent[qiskit]

================
2. Usage Example
================

Typical usage involves specifying a runtime primitive via the :code:`device` argument and specifying an IBM backend via the :code:`backend` argument. An access token from IBM Quantum can be provided explicitly as :code:`ibmqx_token` or in the `Covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_.

The following example shows several :code:`QiskitExecutor` instances being utilized as a Quantum Cluster.

.. code:: python

    import covalent as ct
    import pennylane as qml

    # Default local qiskit executor.
    qiskit_local = ct.executor.QiskitExecutor()

    # Runtime qiskit executor that uses the "ibmq_qasm_simulator" backend.
    qiskit_qasm = ct.executor.QiskitExecutor(
        device="sampler",
        backend="ibmq_qasm_simulator",
        ibmqx_token="<token>",  # required if not in config file
    )

    # Runtime qiskit executor that uses the "ibmq_lima" QPU.
    qiskit_lima = ct.executor.QiskitExecutor(
        device="sampler",
        backend="ibmq_lima",
        ibmqx_token="<token>",
        instance="my-hub/my-group/my-project",

        # Backend settings (optional)
        options={
            "optimization_level": 2,
            "resilience_level": 1,
            # ...
        }
    )

    # Create quantum electron that uses a cluster of 3 qiskit executors.
    @ct.qelectron(executors=[qiskit_local, qiskit_qasm, qiskit_lima])
    @qml.qnode(qml.device("default.qubit", wires=2, shots=1024), interface="tf")
    def circuit(x):
        qml.IQPEmbedding(features=x, wires=[0, 1])
        qml.Hadamard(wires=1)
        return qml.probs(wires=range(2))


One converted to a QElectron, the circuit can be called normally or asynchronously via :code:`circuit.run_later()`. Since the example uses a quantum cluster with the default :code:`"cyclic"` selector, circuit calls will repeatedly cycle through :code:`executors` in order.

A synchronous example is shown below.

.. code:: python

    >>> circuit([0.6, -1.57])  # local

    tf.Tensor([0.0546875  0.42773438 0.46777344 0.04980469], shape=(4,), dtype=float64)

    >>> circuit([0.6, -1.57])  # ibmq_qasm_simulator

    tf.Tensor([0.04589844 0.45507812 0.45898438 0.04003906], shape=(4,), dtype=float64)

    >>> circuit([0.6, -1.57])  # ibmq_lima

    tf.Tensor([0.04199219 0.44628906 0.46679688 0.04492188], shape=(4,), dtype=float64)

    >>> circuit([0.6, -1.57])  # local (again)

    tf.Tensor([0.04394531 0.4609375  0.43945312 0.05566406], shape=(4,), dtype=float64)

If instead doing this asynchronously:

.. code:: python

    >>> x = [0.6, -1.57]

    >>> # Queue jobs for all four circuit calls simultaneously on IBM Quantum.
    >>> # Uses same executor order as above (local, qasm, lima, local, ...).
    >>> futs = [circuit.run_later(x) for _ in range(4)]

    >>> # Wait for all circuits to finish.
    >>> [fut.result() for fut in futs]

    [tf.Tensor([0.0546875  0.42773438 0.46777344 0.04980469], shape=(4,), dtype=float64),
     tf.Tensor([0.04589844 0.45507812 0.45898438 0.04003906], shape=(4,), dtype=float64),
     tf.Tensor([0.04199219 0.44628906 0.46679688 0.04492188], shape=(4,), dtype=float64),
     tf.Tensor([0.04394531 0.4609375  0.43945312 0.05566406], shape=(4,), dtype=float64)]


============================
3. Overview of Configuration
============================

The :code:`QiskitExecutor` configuration is found under :code:`[qelectron.QiskitExecutor]` in the `Covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_.

.. list-table::
    :widths: 2 1 2 3
    :header-rows: 1

    * - Config Key
      - Is Required
      - Default
      - Description
    * - device
      - Yes
      - local_sampler
      - The qiskit (e.g. :code:`"local_sampler"`) or qiskit runtime (e.g. :code:`"sampler"`) primitive used for running circuits on an IBM backend.
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

The following backend settings are also set by default under :code:`[qelectron.QiskitExecutor.options]`. These represent maximum optimization/resilience levels for the :code:`Sampler` primitive. Users can append additional settings to this configuration or specify them directly when instantiating a :code:`QiskitExecutor`. See the `Qiskit Runtime Options <https://qiskit.org/ecosystem/ibm-runtime/stubs/qiskit_ibm_runtime.options.Options.html>`_ page for a complete list of valid fields.

.. list-table::
    :widths: 2 1 2 3
    :header-rows: 1

    * - Config Key
      - Is Required
      - Default
      - Description
    * - optimization_level
      - No
      - 3
      - How much optimization to perform on the circuits.
    * - resilience_level
      - No
      - 1
      - How much resilience to build against errors.

===========================
4. Required Cloud Resources
===========================

In order to access IBM backends, users must acquire an access token from IBM Quantum. This can be done by creating a free account on the `IBM Quantum Experience <https://quantum-computing.ibm.com/>`_.

-----

.. autopydantic_model:: covalent.executor.QiskitExecutor
