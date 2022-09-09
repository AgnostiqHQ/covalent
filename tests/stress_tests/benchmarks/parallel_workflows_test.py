import secrets
import tempfile

import pytest

import covalent as ct


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_parallel_fileio_test(benchmark, iteration):
    run_benchmark, logger = benchmark

    @ct.electron
    def create_delete_tempfile():
        fp = tempfile.NamedTemporaryFile(delete=True)
        # thousand lines per file
        for i in range(1000):
            fp.write(secrets.token_bytes(16384))
        fp.close()

    @ct.lattice
    def parallel_fileio(N: int):
        for i in range(N):
            create_delete_tempfile()

    result, status = run_benchmark(iteration, parallel_fileio, *[50])
    logger.debug(result.dict())

    assert status == "COMPLETED"
