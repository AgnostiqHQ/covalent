from dataclasses import dataclass
from enum import Enum
from typing import Optional

from qiskit.quantum_info import SparsePauliOp
from qiskit_ibm_runtime import Options, options

MEASURE_OP_NAME = "measure"


class _Options:
    def get(self, k, default=None):
        """
        mimics a `dict` object's `get` method using instance's `__dict__`,
        defaults when the value is None
        """
        if k in self.__dict__ and self.__dict__[k]:
            return self.__dict__[k]
        return default


@dataclass(frozen=True)
class RuntimeOptions(_Options):
    """
    Execution options of Qiskit Runtime
    """
    optimization_level: int = 3
    resilience_level: int = 1
    max_execution_time: Optional[int] = None
    transpilation: Optional[options.TranspilationOptions] = None
    resilience: Optional[options.ResilienceOptions] = None
    execution: Optional[options.ExecutionOptions] = None
    environment: Optional[options.EnvironmentOptions] = None
    simulator: Optional[options.SimulatorOptions] = None


class PennylaneQiskitError(Exception):
    """
    For errors related to the Pennylane-to-Qiskit interfacing code
    """


class Measurement(str, Enum):
    """
    Enumeration of Pennylane measurement types.
    see: https://docs.pennylane.ai/en/stable/introduction/measurements.html
    """
    EXPVAL = "expval"
    SAMPLE = "sample"
    COUNTS = "counts"
    VAR = "var"
    PROBS = "probs"
    STATE = "state"
    DENSITY_MATRIX = "density_matrix"
    VN_ENTROPY = "vn_entropy"
    MUTUAL_INFO = "mutual_info"
    PURITY = "purity"
    CLASSICAL_SHADOW = "classical_shadow"
    SHADOW_EXPVAL = "shadow_expval"


def extract_options(opts: dict) -> Options:
    """
    Construct a Qiskit `Options` object from the options dictionary
    """
    _options = Options()
    _options.optimization_level = opts.get("optimization_level", 3)
    _options.resilience_level = opts.get("resilience_level", 1)
    _options.max_execution_time = opts.get("max_execution_time", None)
    _options.transpilation = opts.get("transpilation", _options.transpilation)
    _options.resilience = opts.get("resilience", _options.resilience)
    _options.execution = opts.get("execution", _options.execution)
    _options.environment = opts.get("environment", _options.environment)
    _options.simulator = opts.get("simulator", _options.simulator)
    return _options


def convert_qscripts(compiled_circuits):
    """
    Compile circuits and extract observables
    """
    observables = []

    # extract observables
    for cc in compiled_circuits:

        # instructions are sorted, with measurements at the end; iterate in
        # reverse to avoid looping through preceding instructions
        measure_ops = []
        for circ_instr in reversed(cc.data):
            if circ_instr.operation.name != MEASURE_OP_NAME:
                break

            # remove measurement gate
            measure_ops.append(cc.data.pop(-1))

        # construct a Qiskit `SparsePauliOp` to represent observable
        obs_chars = ["I"] * cc.num_qubits
        for measure_op in reversed(measure_ops):
            for q in measure_op.qubits:
                obs_chars[q.index] = "Z"

        obs_string = "".join(obs_chars)
        observables.append(SparsePauliOp(obs_string))

    return compiled_circuits, observables
