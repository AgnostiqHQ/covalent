from pennylane import QubitDevice, active_return
from pennylane import numpy as np
from pennylane.devices.default_qubit import DefaultQubit

from covalent_qelectron.middleware.core import middleware


class QEDevice(QubitDevice):
    name = "QEDevice"
    short_name = "qe_device"
    pennylane_requires = ">=0.29.1"
    version = "0.0.1"
    author = "aq"

    operations = DefaultQubit.operations
    observables = DefaultQubit.observables

    def __init__(
        self,
        wires=1,
        shots=None,
        *,
        r_dtype=np.float64,
        c_dtype=np.complex128,
        analytic=None,
        executors=None,
        qelectron_info=None,
    ):
        super().__init__(wires, shots, r_dtype=r_dtype, c_dtype=c_dtype, analytic=analytic)

        self._async_run = False
        self._batch_id = None
        self.executors = executors
        self.qelectron_info = qelectron_info

        # This will be set when the QNodeQE
        # is called with args and kwargs
        self.qnode_specs = None

    def apply(self, *args, **kwargs):
        pass

    def batch_execute(self, circuits):

        # Async submit all circuits to middleware which will then submit to the quantum server
        batch_id = middleware.run_circuits_async(
            circuits, self.executors, self.qelectron_info, self.qnode_specs
        )

        # Relevant when `run_later` is used to run the circuit
        # We will retrieve the result later using the future object and the batch_id
        if self._async_run:
            self._batch_id = batch_id
            # Return a dummy result
            return [np.asarray([1]) for _ in circuits]

        # Otherwise, get the results from the middleware
        results = middleware.get_results(batch_id)

        if not active_return():

            if all(len(c.measurements) == 1 for c in circuits):
                results = [
                    [r] if isinstance(r, dict) else np.asarray([r])
                    for r in results
                ]

            if len(circuits) > 1:
                results = [r if isinstance(r, list) else r for r in results]

        return results

    @classmethod
    def capabilities(cls):
        capabilities = super().capabilities().copy()
        capabilities.update(supports_broadcasting=True)
        return capabilities
