from abc import ABC, abstractmethod


class FileTransferStrategy(ABC):
    @abstractmethod
    def download(self, file):
        raise NotImplementedError

    @abstractmethod
    def upload(self, file):
        raise NotImplementedError
