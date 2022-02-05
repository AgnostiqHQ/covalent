# File created by Covalent using covalent version 0.24.1
# Note that this file does not contain any global imports you did in your original dispatch
# Covalent result - -0.9899924966004454

# Result of dispatch ae995d53-5503-448e-b21b-4649db02e135
# Result status: COMPLETED
# Result start time: 2022-02-05 04:00:22.157664+00:00
# Result end time: 2022-02-05 04:00:22.295183+00:00


import builtins as __builtin__
import builtins as __builtins__
import os as os
import sys as sys

import matplotlib as matplotlib
import numpy as np

# import covalent as something_really_long
# import covalent as covalent
import pennylane as qml


# @something_really_long.electron()
@qml.qnode(qml.device("default.qubit", wires=2))
def identity(x):
    qml.RX(x, wires=0)
    return qml.expval(qml.PauliZ(0))


# @covalent.lattice
def workflow(x):
    return identity(x)


if __name__ == "__main__":
    workflow(x=3)
