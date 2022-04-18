from app.core.config import settings
from furl import furl


class ServiceURI:
    def __init__(
        self, scheme: str = "http", host: str = "localhost", port=None, preffix="api/v0"
    ) -> None:
        self.scheme = scheme
        self.host = host
        self.port = port
        self.preffix = preffix

    def get_base_url(self):
        base_url = furl().set(scheme=self.scheme, host=self.host, port=self.port)
        if self.preffix:
            base_url.set(path=self.preffix)
        return base_url

    def get_route(self, path: str):
        base_url = self.get_base_url().copy()
        base_url.path /= path
        return base_url.url


class RunnerURI(ServiceURI):
    def __init__(self) -> None:
        super().__init__(port=settings.RUNNER_SVC_PORT, host=settings.RUNNER_SVC_HOST)


class ResultsURI(ServiceURI):
    def __init__(self) -> None:
        super().__init__(port=settings.RESULTS_SVC_PORT, host=settings.RESULTS_SVC_HOST)


class DispatcherURI(ServiceURI):
    def __init__(self) -> None:
        super().__init__(port=settings.DISPATCHER_SVC_PORT, host=settings.DISPATCHER_SVC_HOST)
