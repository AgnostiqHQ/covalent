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

"""Unit tests for result serializer"""

import tempfile
from datetime import datetime, timezone

import covalent as ct
from covalent._results_manager.result import Result
from covalent._serialize.result import deserialize_result, serialize_result


def test_serialize_deserialize_result():
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
    result_object = Result(workflow)
    ts = datetime.now(timezone.utc)
    result_object._start_time = ts
    result_object._end_time = ts
    with tempfile.TemporaryDirectory() as d:
        manifest = serialize_result(result_object, d)
        res = deserialize_result(manifest)

        assert res._start_time == ts
        assert res._end_time == ts
        assert res.inputs == res.lattice.inputs
        assert len(res.inputs.get_deserialized()["args"]) == 2

        tg1 = result_object.lattice.transport_graph
        tg2 = res.lattice.transport_graph

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


def reset_metadata():
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
    result_object = Result(workflow)
    ts = datetime.now(timezone.utc)
    result_object._start_time = ts
    result_object._end_time = ts
    result_object.lattice.transport_graph.set_node_value(0, "status", Result.COMPLETED)
    with tempfile.TemporaryDirectory() as d:
        manifest = serialize_result(result_object, d)

        manifest.reset_metadata()

        assert manifest.metadata.status == str(Result.NEW_OBJ)

        assert manifest.metadata.start_time is None
        assert manifest.metadata.end_time is None

        tg = manifest.lattice.transport_graph
        for i in tg.nodes:
            assert tg.nodes[i].metadata.status == str(Result.NEW_OBJ)
            assert tg.nodes[i].metadata.start_time is None
            assert tg.nodes[i].metadata.end_time is None
