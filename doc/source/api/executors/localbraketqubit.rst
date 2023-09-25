
Local Braket Qubit Executor
"""""""""""""

This quantum executor accesses the local Braket quantum circuit simulator (:code:`"braket.local.qubit"`).

It utilizes the Pennylane plugin found `here <https://amazon-braket-pennylane-plugin-python.readthedocs.io/en/latest/>`_.
:code:`LocalBraketQubitExecutor` introduces thread-based parallelism for circuit execution on the :code:`"braket.local.qubit"` device.

===============
1. Installation
===============

:code:`LocalBraketQubitExecutor` is not included in base Covalent.
To use it, you will need to install the Covalent with:

.. code:: console

    pip install covalent[braket]

================
2. Usage Example
================

Using :code:`LocalBraketQubitExecutor` is simple:

.. code:: python

    # Local simulator
    executor = ct.executor.LocalBraketQubitExecutor(
        device="default",
        shots=1024,
        num_threads=2
    )

    @ct.qelectron(executors=executor)
    @qml.qnode(qml.device("default.qubit", wires=2, shots=1024))
    def circuit(x):
        qml.IQPEmbedding(features=x, wires=[0, 1])
        qml.Hadamard(wires=1)
        return [qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))]

As a QElectron, the circuit can be called either normally or asynchronously using :code:`circuit.run_later()`.

Synchronous example output is below

.. code:: python

    >>> print(circuit([0.5, 0.1]))

    [array(0.008), array(0.996)]


and asynchronously:

.. code:: python

    >>> x = [0.6, -1.57]

    >>> # Queue jobs for all three circuit calls simultaneously on.
    >>> futs = [circuit.run_later(x) for _ in range(3)]

    >>> # Wait for all circuits to finish.
    >>> [fut.result() for fut in futs]

    [[array(-0.02), array(0.01)],
     [array(0.014), array(-0.022)],
     [array(-0.074), array(0.05)]]

============================
3. Overview of Configuration
============================

The :code:`LocalBraketQubitExecutor` configuration is found under :code:`[qelectron.LocalBraketQubitExecutor]` in the `Covalent configuration file <https://covalent.readthedocs.io/en/latest/how_to/config/customization.html>`_.

.. list-table::
    :widths: 2 1 2 3
    :header-rows: 1

    * - Config Key
      - Is Required
      - Default
      - Description
    * - backend
      - No
      - "default"
      - The type of simulator backend to be used. Choices are :code:`"default"`, :code:`"braket_sv"`, :code:`"braket_dm"` and :code:`"braket_ahs"`.


-----

.. autopydantic_model:: covalent.executor.LocalBraketQubitExecutor
