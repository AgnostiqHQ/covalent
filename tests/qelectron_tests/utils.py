"""
Misc. utilities for QElectron tests.
"""
from typing import Callable
import pennylane as qml

_MEASUREMENTS_MAP = {
    "expval": qml.expval,
    "var": qml.var,
    "sample": qml.sample,
    "probs": qml.probs,
}


def get_named_measurement(meas_name: str) -> Callable:
    """
    Helps parametrize QElectron tests over Pennylane measurement types.
    """
    if (meas := _MEASUREMENTS_MAP.get(meas_name)) is None:
        raise ValueError(f"Invalid measurement name: {meas_name}")
    return meas
