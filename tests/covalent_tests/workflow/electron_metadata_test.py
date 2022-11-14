# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

"""Unit tests to test whether electrons inherit lattice metadata correctly"""

import json


def test_electrons_get_lattice_metadata_1():
    """case 1: test explicit electron metadata always wins"""
    import covalent as ct

    electron_bash_dep = ct.DepsBash(["yum install rustc"])
    lattice_bash_dep = ct.DepsBash(["yum install kernel"])

    # Construct tasks as "electrons"
    @ct.electron(executor="electron_executor", deps_bash=electron_bash_dep)
    def join_words(a, b):
        return ", ".join([a, b])

    @ct.electron(executor="electron_executor", deps_bash=electron_bash_dep)
    def excitement(a):
        return f"{a}!"

    # Construct a workflow of tasks
    @ct.lattice(executor="awslambda", deps_bash=lattice_bash_dep)
    def hello_world(a, b):
        """This is a basic hello world dispatch"""
        phrase = join_words(a, b)
        return excitement(phrase)

    # Dispatch the workflow
    hello_world.build_graph("hello", "world")

    data = hello_world.transport_graph.serialize_to_json()
    data = json.loads(data)

    for i in data["nodes"]:
        if "parameter" not in i["name"]:
            assert i["metadata"]["executor"] == "electron_executor"
            assert i["metadata"]["deps"]["bash"] == electron_bash_dep.to_dict()


def test_electrons_get_lattice_metadata_2():
    """case 2: electron with unset metadata inherits lattice metadata"""
    import covalent as ct

    electron_bash_dep = ct.DepsBash(["yum install rustc"])
    lattice_bash_dep = ct.DepsBash(["yum install kernel"])

    # Construct tasks as "electrons"
    @ct.electron
    def join_words(a, b):
        return ", ".join([a, b])

    @ct.electron
    def excitement(a):
        return f"{a}!"

    # Construct a workflow of tasks
    @ct.lattice(executor="lattice_executor", deps_bash=lattice_bash_dep)
    def hello_world(a, b):
        """This is a basic hello world dispatch"""
        phrase = join_words(a, b)
        return excitement(phrase)

    # Dispatch the workflow
    hello_world.build_graph("hello", "world")

    data = hello_world.transport_graph.serialize_to_json()
    data = json.loads(data)

    for i in data["nodes"]:
        if "parameter" not in i["name"]:
            assert i["metadata"]["executor"] == "lattice_executor"
            assert i["metadata"]["deps"]["bash"] == lattice_bash_dep.to_dict()
