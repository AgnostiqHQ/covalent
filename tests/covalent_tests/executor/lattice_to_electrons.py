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

"""Unit tests to check that electrons inherit the parent lattice executor."""

import json

import covalent as ct
from covalent._workflow.lattice import Lattice as LatticeClass


def test_electrons_have_lattice_executor():
    """start the covalent server with local executor and then run this program."""
    import covalent as ct

    # Construct tasks as "electrons"
    @ct.electron
    def join_words(a, b):
        return ", ".join([a, b])

    @ct.electron
    def excitement(a):
        return f"{a}!"

    # Construct a workflow of tasks
    @ct.lattice(executor="dask")
    def hello_world(a, b):
        """This is a basic hello world dispatch"""
        phrase = join_words(a, b)
        return excitement(phrase)

    # Dispatch the workflow
    hello_world.build_graph("hello", "world")
    data = hello_world.transport_graph.serialize_to_json()
    data = json.loads(data)
    hello_world = LatticeClass.deserialize_from_json(hello_world.serialize_to_json())

    for i in data["nodes"]:
        if "parameter" not in i["name"]:
            assert i["metadata"]["executor"] == hello_world.metadata["executor"]


def test_electrons_precede_lattice_executor():
    import covalent as ct

    # Construct tasks as "electrons"
    @ct.electron
    def join_words(a, b):
        return ", ".join([a, b])

    @ct.electron(executor="local")
    def excitement(a):
        return f"{a}!"

    # Construct a workflow of tasks
    @ct.lattice(executor="dask")
    def hello_world(a, b):
        """This is a basic hello world dispatch"""
        phrase = join_words(a, b)
        return excitement(phrase)

    # Dispatch the workflow
    hello_world.build_graph("hello", "world")
    data = hello_world.transport_graph.serialize_to_json()
    data = json.loads(data)
    hello_world = LatticeClass.deserialize_from_json(hello_world.serialize_to_json())

    for i in data["nodes"]:
        if ("parameter" not in i["name"]) and ("excitement" in i["name"]):
            assert i["metadata"]["executor"] == "local"
        elif "parameter" not in i["name"]:
            assert i["metadata"]["executor"] == hello_world.metadata["executor"]
