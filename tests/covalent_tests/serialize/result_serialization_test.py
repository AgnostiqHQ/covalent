# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for result serializer"""

import copy
import tempfile
from datetime import datetime, timezone

import covalent as ct
from covalent._results_manager.result import Result
from covalent._serialize.result import (
    deserialize_result,
    extract_assets,
    merge_response_manifest,
    serialize_result,
)


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


def test_reset_metadata():
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
        for node in tg.nodes:
            assert node.metadata.status == str(Result.NEW_OBJ)
            assert node.metadata.start_time is None
            assert node.metadata.end_time is None


def test_merge_dispatcher_response():
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
    returned_manifest = copy.deepcopy(manifest)

    result_asset = returned_manifest.assets.result
    result_asset.remote_uri = "result_asset_upload_url"

    tg = returned_manifest.lattice.transport_graph
    for node in tg.nodes:
        function_asset = node.assets.function
        function_asset.remote_uri = "node_asset_upload_url"

    merged = merge_response_manifest(manifest, returned_manifest)

    assert merged.assets.result.remote_uri == "result_asset_upload_url"

    for node in merged.lattice.transport_graph.nodes:
        assert node.assets.function.remote_uri == "node_asset_upload_url"


def test_extract_assets():
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

    all_assets = extract_assets(manifest)

    asset_count = 0
    for key, asset in manifest.assets:
        asset_count += 1

    for key, asset in manifest.lattice.assets:
        asset_count += 1

    for node in manifest.lattice.transport_graph.nodes:
        for key, asset in node.assets:
            asset_count += 1

    assert len(all_assets) == asset_count
