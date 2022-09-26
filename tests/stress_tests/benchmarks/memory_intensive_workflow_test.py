import numpy as np
import pytest

import covalent as ct
from covalent._shared_files.util_classes import Status


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_matrix_multiplication(benchmark, iteration):
    run_benchmark = benchmark[0]
    logger = benchmark[1]
    arraysizes = [128, 256, 512, 1024]

    @ct.electron
    def create_matrix(arraysize: int):
        return np.random.random((arraysize, arraysize))

    @ct.electron
    def matrix_multiply(a: np.ndarray, b: np.ndarray):
        return np.matmul(a, b)

    @ct.lattice
    def matrix_multiplication(arraysizes):
        for arraysize in arraysizes:
            a = create_matrix(arraysize)
            b = create_matrix(arraysize)
            matrix_multiply(a, b)
        arraysizes = [256, 512, 1024]

    results, status = run_benchmark(iteration, matrix_multiplication, *[arraysizes])
    logger.debug(results.dict())

    assert status == Status("COMPLETED")
