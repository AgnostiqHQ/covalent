import zerorpc
from covalent_qelectron.shared_utils import cloudpickle_serialize, cloudpickle_deserialize
from covalent_qelectron.middleware.qclients import LocalQClient

class RPCQClient(LocalQClient):
    def __init__(self) -> None:
        # This is because when using RPC the client object
        # object behaves as if it's the server object out of the box
        self.qserver = zerorpc.Client()
        self.qserver.connect("tcp://127.0.0.1:4242")

    def serialize(self, obj):
        return cloudpickle_serialize(obj)

    def deserialize(self, obj):
        return cloudpickle_deserialize(obj)
