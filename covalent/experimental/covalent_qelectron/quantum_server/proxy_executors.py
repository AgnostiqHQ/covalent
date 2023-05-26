from covalent_qelectron.executors.base import *
from covalent_qelectron.executors.plugins import *
from covalent_qelectron.executors.clusters import *


# Ways to add new methods/attributes to the executor classes:

# 1. Inherit from the class and add new methods/attributes:

# class Simulator(Simulator):
#     def my_method(self):
#         print("Hello World")

# 2. Assign directly to the class, but it also modifies
# the original class, so it's better for remote server case:

# Simulator.my_method = lambda self: print("Hello World")
