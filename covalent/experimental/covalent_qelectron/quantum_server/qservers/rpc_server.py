import zerorpc
from covalent_qelectron.quantum_server import QServer
from covalent_qelectron.shared_utils import cloudpickle_serialize, cloudpickle_deserialize


class RPCQServer(QServer):
    def serialize(self, obj):
        return cloudpickle_serialize(obj)

    def deserialize(self, obj):
        return cloudpickle_deserialize(obj)



if __name__ == "__main__":
    s = zerorpc.Server(RPCQServer())
    s.bind("tcp://0.0.0.0:4242")
    s.run()
