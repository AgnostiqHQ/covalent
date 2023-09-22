# QElectron Tests

This tests package is a work in progress.

It is designed to run the Pennylane test suite by patching the `QNode` class to
call a `QNodeQE` instance (*i.e.* a QElectron).

## Cloning Pennylane tests

One can clone the Pennylane test suite using the scripts provided `scripts/`:

```
cd scripts
bash clone_qml_tests.sh v0.30.0
```

This above will create a folder `qelectron_tests/pennylane_test-v0.30.0/` that contains
the Pennylane test suite.

## Running Pennylane tests on QElectrons

One must also point to the configuration file (`qelectron_tests/conftest.py`)
to apply the required patches and fixtures. An example is given below:

```
cd covalent-os-private/tests
pytest -c qelectron_tests/conftest.py qelectron_tests/pennylane_tests-v0.30.0/test_return_types_qnode.py
```

To run the *entire* test suite, do the following:

```
cd covalent-os-private/tests
pytest -c qelectron_tests/conftest.py qelectron_tests/pennylane_tests-v0.30.0/
```
