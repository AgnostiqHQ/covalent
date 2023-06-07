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

"""Unit tests for lattice serializer"""

import platform
import tempfile

import covalent as ct
from covalent._serialize.lattice import deserialize_lattice, serialize_lattice


def test_serialize_deserialize_lattice():
    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def add(x, y):
        return x + y

    @ct.lattice
    def workflow(x, y):
        res1 = identity(x)
        res2 = identity(y)
        return add(res1, res2)

    workflow.build_graph(2, 3)
    with tempfile.TemporaryDirectory() as d:
        model = serialize_lattice(workflow, d)
        assert model.metadata.python_version == platform.python_version()
        assert model.metadata.covalent_version == ct.__version__
        lat = deserialize_lattice(model)

        lat.inputs = lat.inputs.get_deserialized()
        assert lat.inputs["args"][0] == 2
        assert lat.inputs["args"][1] == 3

        tg1 = workflow.transport_graph
        tg2 = lat.transport_graph

        assert set(tg1._graph.nodes) == set(tg2._graph.nodes)
        assert set(tg1._graph.edges) == set(tg2._graph.edges)

        for node in tg1._graph.nodes:
            assert tg1._graph.nodes[node].keys() <= tg2._graph.nodes[node].keys()
            assert (
                tg1._graph.nodes[node]["function"].get_serialized()
                == tg2._graph.nodes[node]["function"].get_serialized()
            )

        for edge in tg1._graph.edges:
            assert tg1._graph.edges[edge].items() <= tg2._graph.edges[edge].items()


def test_serialize_lattice_custom_assets():
    @ct.electron
    def identity(x):
        return x

    @ct.electron
    def add(x, y):
        return x + y

    @ct.lattice
    def workflow(x, y):
        res1 = identity(x)
        res2 = identity(y)
        return add(res1, res2)

    workflow.metadata["custom_asset_keys"] = ["custom_lat_asset"]

    workflow.build_graph(2, 3)
    node_metadata = workflow.transport_graph.get_node_value(0, "metadata")
    node_metadata["custom_asset_keys"] = ["custom_electron_asset"]

    with tempfile.TemporaryDirectory() as d:
        manifest = serialize_lattice(workflow, d)
        assert ["custom_lat_asset"] == list(manifest.custom_assets.keys())

        node_0 = manifest.transport_graph.nodes[0]
        assert "custom_electron_asset" in node_0.custom_assets

        node_1 = manifest.transport_graph.nodes[1]
        assert not node_1.custom_assets
