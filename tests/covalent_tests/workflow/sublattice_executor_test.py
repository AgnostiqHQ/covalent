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

"""Unit tests to check that sublattices inherit the parent lattice executor."""

import json

import covalent as ct


def test_sublattices_have_default_executor():
    """start the covalent server with dask, and don't specify executor to main lattice.
    This is to check if everything has dask, including sublattices."""
    import covalent as ct

    @ct.electron
    def add(a, b):
        return a + b

    @ct.electron
    def sub(a, b):
        return a - b

    @ct.electron
    @ct.lattice
    def mul(a, b):
        res1 = add(a, b)
        res2 = sub(a, b)
        return res1, res2

    @ct.electron
    @ct.lattice
    def div(a, b):
        a = add(a, b)
        b = sub(a, b)
        return a / b

    @ct.lattice
    def solution(a, b):
        res1, res2 = mul(a, b)
        sol = div(res1, res2)
        return sol

    # Dispatch the workflow
    solution.build_graph(3, 2)
    data = solution.transport_graph.serialize_to_json()
    data = json.loads(data)

    for i in data["nodes"]:
        if "sublattice" in i["name"]:
            assert i["metadata"]["executor"] == "dask"


def test_sublattices_have_lattice_executor():
    """start the covalent server with dask, and change the executor to local.
    This checks that sublattices executor should be local."""
    import covalent as ct

    @ct.electron
    def add(a, b):
        return a + b

    @ct.electron
    def sub(a, b):
        return a - b

    @ct.electron
    @ct.lattice
    def mul(a, b):
        res1 = add(a, b)
        res2 = sub(a, b)
        return res1, res2

    @ct.electron
    @ct.lattice
    def div(a, b):
        a = add(a, b)
        b = sub(a, b)
        return a / b

    @ct.lattice(executor="local")
    def solution(a, b):
        res1, res2 = mul(a, b)
        sol = div(res1, res2)
        return sol

    # Dispatch the workflow
    solution.build_graph(3, 2)
    data = solution.transport_graph.serialize_to_json()
    data = json.loads(data)

    for i in data["nodes"]:
        if "sublattice" in i["name"]:
            assert i["metadata"]["executor"] == "local"


def test_sublattices_precede_lattice_executor():
    """Start covalent server with dask, Change a sublattice executor.
    Now it shouldn't take the lattice executor."""
    import covalent as ct

    @ct.electron
    def add(a, b):
        return a + b

    @ct.electron
    def sub(a, b):
        return a - b

    @ct.electron
    @ct.lattice
    def mul(a, b):
        res1 = add(a, b)
        res2 = sub(a, b)
        return res1, res2

    @ct.electron(executor="dask")
    @ct.lattice
    def div(a, b):
        a = add(a, b)
        b = sub(a, b)
        return a / b

    @ct.lattice(executor="local")
    def solution(a, b):
        res1, res2 = mul(a, b)
        sol = div(res1, res2)
        return sol

    # Dispatch the workflow
    solution.build_graph(3, 2)
    data = solution.transport_graph.serialize_to_json()
    data = json.loads(data)

    for i in data["nodes"]:
        if ("div" in i["name"]) and ("sublattice" in i["name"]):
            assert i["metadata"]["executor"] == "dask"
        elif "sublattice" in i["name"]:
            assert i["metadata"]["executor"] == "local"
