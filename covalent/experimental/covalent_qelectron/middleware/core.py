import pennylane as qml
from typing import List
from covalent_qelectron.middleware.qclients import LocalQClient


class MiddleWare:

    def __init__(self) -> None:
        self.qclient = LocalQClient()

    def __new__(cls):
        # Making this a singleton class
        if not hasattr(cls, 'instance'):
            cls.instance = super(MiddleWare, cls).__new__(cls)
        return cls.instance

    # The following attributes are properties
    # because the qclient might change over time
    # and every time it gets changed, we shouldn't
    # have to set things like:
    # self.database = self.qclient.database
    # Thus, we override the access of these attributes
    # and return/set these dynamically depending upon
    # what the qclient is at that point in time.

    @property
    def selector(self):
        return self.qclient.selector

    @selector.setter
    def selector(self, selector_func):
        self.qclient.selector = selector_func

    @property
    def database(self):
        return self.qclient.database

    def run_circuits_async(
            self, qscripts: List[qml.tape.qscript.QuantumScript], executors, qelectron_info, qnode_specs):
        return self.qclient.submit(qscripts, executors, qelectron_info, qnode_specs)

    def get_results(self, batch_id):
        return self.qclient.get_results(batch_id)


middleware = MiddleWare()
