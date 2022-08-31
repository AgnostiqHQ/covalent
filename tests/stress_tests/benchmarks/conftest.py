import logging
import time

import pytest

import covalent as ct
from covalent._shared_files.metrics import PerformanceMetrics, WorkflowBenchmarkResult


def run_benchmark(benchmark_id: int, lattice, *args, **kwargs):
    """
    Benchmark the lattice using against a Covalent server
    """
    # Run as normal function
    start = time.time()
    lattice(*args, **kwargs)
    end = time.time()
    normal_runtime = end - start

    # Dispatch to Covalent
    dispatch_id = ct.dispatch(lattice)(*args, **kwargs)
    dispatch_result = ct.get_result(dispatch_id=dispatch_id, wait=True)
    covalent_execution_time = (
        dispatch_result.end_time - dispatch_result.start_time
    ).total_seconds()

    # Covalent overhead (relative increase)
    overhead = (covalent_execution_time - normal_runtime) / normal_runtime

    metrics = PerformanceMetrics(
        workflow_runtime=normal_runtime,
        covalent_runtime=covalent_execution_time,
        covalent_speedup=normal_runtime / covalent_execution_time,
        covalent_overhead=overhead,
    )

    return (
        WorkflowBenchmarkResult(
            run_id=benchmark_id, workflow_name=lattice.__name__, metrics=metrics
        ),
        dispatch_result.status,
    )


@pytest.fixture(scope="module")
def benchmark():
    logger = logging.getLogger("metricsLogger")
    logger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler("metrics.log")
    fileHandler.setFormatter(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s")
    fileHandler.setFormatter(formatter)

    logger.addHandler(fileHandler)
    yield (
        run_benchmark,
        logger,
    )
