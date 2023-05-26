import zerorpc

from ...quantum_server import QServer
from ...shared_utils import cloudpickle_deserialize, cloudpickle_serialize


class RPCQServer(QServer):
    def serialize(self, obj):
        return cloudpickle_serialize(obj)

    def deserialize(self, obj):
        return cloudpickle_deserialize(obj)


if __name__ == "__main__":
    s = zerorpc.Server(RPCQServer())
    s.bind("tcp://0.0.0.0:4242")
    s.run()
