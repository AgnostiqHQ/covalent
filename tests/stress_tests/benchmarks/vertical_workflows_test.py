import time

import pytest

import covalent as ct


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_fully_vertical_add_workflow(benchmark, iteration):
    run_benchmark, logger = benchmark

    @ct.electron
    def add(x: int, y: int):
        return x + y

    @ct.lattice
    def vertical_add_workflow(N: int):
        for i in range(N):
            if i == 0:
                r1 = add(1, 1)
            else:
                r1 = add(r1, 1)
        return r1

    result, status = run_benchmark(iteration, vertical_add_workflow, *[50])
    logger.debug(result.dict())

    assert status == "COMPLETED"


@pytest.mark.parametrize("iteration", range(5))
def test_benchmark_fully_vertical_multiply_workflow(benchmark, iteration):
    run_benchmark, logger = benchmark

    @ct.electron
    def multiply(x: int, y: int):
        return x + y

    @ct.lattice
    def vertical_multiply_workflow(N: int):
        for i in range(N):
            if i == 0:
                r1 = multiply(2, 2)
            else:
                r1 = multiply(r1, 2)
        return r1

    result, status = run_benchmark(iteration, vertical_multiply_workflow, *[50])
    logger.debug(result.dict())

    assert status == "COMPLETED"
