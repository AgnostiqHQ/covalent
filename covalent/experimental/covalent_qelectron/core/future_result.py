from ..middleware.core import middleware


class QNodeFutureResult:

    def __init__(self, batch_id):
        self.batch_id = batch_id
        self._result = None

    def result(self):
        """
        Retrieve the results from middleware for the given batch_id.

        Returns:
            Any: The results of the circuit execution.
        """

        if self._result is not None:
            return self._result

        results = middleware.get_results(self.batch_id)

        self._result = results[0].squeeze()
        return self._result
