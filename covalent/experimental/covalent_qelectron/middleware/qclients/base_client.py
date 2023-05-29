from abc import ABC, abstractmethod, abstractproperty


class BaseQClient(ABC):
    @abstractmethod
    def submit(self, qscripts, executors):
        raise NotImplementedError
    
    @abstractmethod
    def get_results(self, future_ids):
        raise NotImplementedError
    
    @abstractproperty
    def selector(self):
        raise NotImplementedError

    @abstractproperty
    def database(self):
        raise NotImplementedError
    
    # The following methods are abstract because the qserver
    # is expecting serialized inputs and will be sending
    # back serialized outputs, thus even if these methods
    # essentially just pass through, for e.g in the LocalQClient's
    # case, they are still to be implemented by the child class and
    # should use the same seriliazing/deserializing method as is being
    # used by the equivalent qserver.
    @abstractmethod
    def serialize(self, obj):
        raise NotImplementedError
    
    @abstractmethod
    def deserialize(self, ser_obj):
        raise NotImplementedError
