Simulator
"""""""""

This quantum executor introduces thread- or process-based parallelism to Pennylane circuits that utilize simulation-based devices (like :code:`"default.qubit"` or :code:`"lightning.qubit"`).

===============
1. Installation
===============

No additional installation is required.

================
2. Usage Example
================

A thread-based :code:`Simulator` is the default quantum executor for QElectrons.

.. code:: python

    import covalent as ct
    import pennylane as qml

    @ct.qelectron
    @qml.qnode(qml.device("lightning.qubit", wires=2), interface="torch")
    def circuit(x):
        qml.IQPEmbedding(features=x, wires=[0, 1])
        qml.Hadamard(wires=1)
        return qml.probs(wires=range(2))

Once converted to a QElectron, the circuit can be called either normally or asynchronously via :code:`circuit.run_later()`.

A synchronous example is show below.

.. code:: python

    >>> circuit([1.3, -0.7]), circuit([1.3, -0.7])

    (tensor([0.3169, 0.3169, 0.1831, 0.1831], dtype=torch.float64),
     tensor([0.3169, 0.3169, 0.1831, 0.1831], dtype=torch.float64))

Alternatively, doing this asynchronously:

.. code:: python

    >>> # Use separate threads to run two circuits simultaneously.
    >>> futs = [circuit.run_later([1.3, -0.7]) for _ in range(2)]

    # Wait for all circuits to finish.
    >>> [fut.result() for fut in futs]

    [tensor([0.3169, 0.3169, 0.1831, 0.1831], dtype=torch.float64),
     tensor([0.3169, 0.3169, 0.1831, 0.1831], dtype=torch.float64)]

-----

.. autopydantic_model:: covalent.executor.Simulator
