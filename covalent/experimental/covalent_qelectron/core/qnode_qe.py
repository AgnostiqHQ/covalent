from contextlib import contextmanager
from typing import Dict, Optional

import pennylane as qml
from pydantic import BaseModel

from ..core.device import QEDevice
from ..core.future_result import QNodeFutureResult


class QNodeSpecs(BaseModel):
    gate_sizes: Dict[str, int]
    gate_types: Dict[str, int]
    num_operations: int
    num_observables: int
    num_diagonalizing_gates: int
    num_used_wires: int
    depth: int
    num_trainable_params: int = None
    num_device_wires: int
    device_name: str
    diff_method: Optional[str]
    expansion_strategy: str
    gradient_options: Dict[str, int]
    interface: Optional[str]
    gradient_fn: Optional[str]
    num_gradient_executions: int = 0
    num_parameter_shift_executions: int = None


class QNodeQE(qml.QNode):
    """
        Initialize a QElectron instance from a given QNode and Executor.

        Args:
            qnode (qml.QNode): The QNode to wrap.
            executors (Executor): The executors to choose from to use for running the QNode.
    """

    def __init__(self, qnode: qml.QNode, executors, qelectron_info):
        self.original_qnode = qnode

        # Create a new device for every QNodeQE instance
        super().__init__(
            func=self.original_qnode.func,
            device=QEDevice(
                wires=self.original_qnode.device.num_wires,
                shots=self.original_qnode.device.shots,
                executors=executors,
                qelectron_info=qelectron_info,
            ),
            interface=self.original_qnode.interface,
            diff_method=self.original_qnode.diff_method,
            expansion_strategy=self.original_qnode.expansion_strategy,
            max_expansion=self.original_qnode.max_expansion,
        )

    @contextmanager
    def mark_call_async(self):
        self.device._async_run = True
        try:
            yield
        finally:
            self.device._async_run = False
            self.device._batch_id = None

    def run_later(self, *args, **kwargs):
        """
        Run the QNode asynchronously.

        Args:
            *args: Positional arguments to pass to the QNode.
            **kwargs: Keyword arguments to pass to the QNode.

        Returns:
            FutureResult: A wrapper object for the async result of running the QNode.
        """

        with self.mark_call_async():
            self(*args, **kwargs)
            batch_id = self.device._batch_id

        return QNodeFutureResult(batch_id)

    def __call__(self, *args, **kwargs):

        self.device.qnode_specs = QNodeSpecs(**qml.specs(self)(*args, **kwargs))
        return super().__call__(*args, **kwargs)
