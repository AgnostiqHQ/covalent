import pytest

import covalent as ct
from covalent._shared_files.util_classes import Status


@pytest.mark.parametrize("iteration", range(5))
def test_add_multiply_workflow(benchmark, iteration: int):
    print(iteration)
    run_benchmark = benchmark[0]
    logger = benchmark[1]

    @ct.electron
    def add(x, y):
        return x + y

    @ct.electron
    def multiply(x, y):
        return x * y

    @ct.lattice
    def add_multiply_workflow(x, y):
        r1 = add(x, y)
        r2 = multiply(r1, y)
        return r2

    metrics, dispatch_status = run_benchmark(iteration, add_multiply_workflow, *[1, 2])
    logger.debug(metrics.dict())

    assert dispatch_status == Status("COMPLETED")
