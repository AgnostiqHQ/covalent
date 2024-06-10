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

import covalent as ct
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import encode_metadata
from covalent.executor import LocalExecutor
from covalent.triggers import BaseTrigger

le = LocalExecutor(log_stdout="/tmp/stdout.log")


def test_lattice_metadata_is_serialized_early():
    """Test that lattice metadata is serialized by the decorator"""

    def identity(y):
        return y

    calldep = ct.DepsCall(identity, args=[5], retval_keyword="y")

    @ct.lattice(
        executor=LocalExecutor(),
        workflow_executor=LocalExecutor(),
        call_before=[calldep],
        call_after=[calldep],
        triggers=BaseTrigger(),
    )
    def workflow(x):
        return 1

    metadata = workflow.metadata
    assert metadata == encode_metadata(metadata)


def test_lattice_json_serialization():
    @ct.electron(executor="le", deps_bash=ct.DepsBash("yum install gcc"))
    def f(x):
        return x * x

    @ct.lattice(executor="le")
    def workflow(x):
        return f(x)

    workflow.build_graph(5)

    json_workflow = workflow.serialize_to_json()

    new_workflow = Lattice.deserialize_from_json(json_workflow)

    for key in workflow.__dict__:
        if key in ["metadata", "transport_graph"]:
            continue
        assert workflow.__dict__[key] == new_workflow.__dict__[key]

    assert (
        workflow.transport_graph.serialize_to_json()
        == new_workflow.transport_graph.serialize_to_json()
    )

    assert json_workflow == new_workflow.serialize_to_json()
