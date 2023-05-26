import functools

from pydantic import BaseModel

from ..core.qnode_qe import QNodeQE
from ..executors import Simulator
from ..executors.base import AsyncBaseQCluster


class QElectronInfo(BaseModel):
    # TODO: fix serialization/deserialization
    # iterating returns name-value tuples, which have no `.json()`
    # see: covalent_qelectron/shared_utils/utils.py
    name: str
    description: str = None


def qelectron(qnode=None, *, executors=None, name=None, description=None):
    """
    Decorator for extending a given QNode.

    Args:
        qnode: The QNode to wrap.
        executors: The executors to choose from to use for running the QNode.
        name: The name of the QElectron. Defaults to the name of the function.
        description: A description of the QElectron. Defaults to the docstring of the function.

    Returns:
        QNodeQE: A QNodeQE instance.
    """

    if executors is None:
        executors = Simulator()

    # check is executor is a QCluster
    if isinstance(executors, AsyncBaseQCluster):
        executors.serialize_selector()

    # check if executor is a list of executors
    if not isinstance(executors, list):
        executors = [executors]

    if qnode is None:
        return functools.partial(qelectron, executors=executors, name=name, description=description)

    if name is None:
        name = qnode.func.__name__

    if description is None:
        description = qnode.func.__doc__

    qelectron_info = QElectronInfo(name=name, description=description)

    # Create a new QNodeQE instance for every qelectron call
    return QNodeQE(qnode, executors, qelectron_info)
