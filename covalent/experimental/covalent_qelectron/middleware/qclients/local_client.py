from covalent_qelectron.middleware.qclients import BaseQClient
from covalent_qelectron.quantum_server.qservers import LocalQServer
from covalent_qelectron.shared_utils import dummy_serialize, dummy_deserialize

# Since in the local case, the server and client are the same
# thus the "server" class's functions are directly accessed


class LocalQClient(BaseQClient):
    def __init__(self) -> None:
        self.qserver = LocalQServer()

    @property
    def selector(self):
        return self.deserialize(self.qserver.selector)

    @selector.setter
    def selector(self, selector_func):
        self.qserver.selector = self.serialize(selector_func)

    @property
    def database(self):
        return self.deserialize(self.qserver.database)

    def submit(self, qscripts, executors, qelectron_info, qnode_specs):
        ser_qscripts = self.serialize(qscripts)
        ser_executors = self.serialize(executors)
        ser_qelectron_info = self.serialize(qelectron_info)
        ser_qnode_specs = self.serialize(qnode_specs)

        return self.qserver.submit(ser_qscripts, ser_executors, ser_qelectron_info, ser_qnode_specs)

    def get_results(self, batch_id):
        ser_results = self.qserver.get_results(batch_id)
        return self.deserialize(ser_results)

    def serialize(self, obj):
        return dummy_serialize(obj)

    def deserialize(self, ser_obj):
        return dummy_deserialize(ser_obj)
