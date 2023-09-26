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

"""Unit tests to test whether electrons inherit lattice metadata correctly"""

import json

from covalent._shared_files.defaults import get_default_executor, postprocess_prefix


def test_electrons_get_lattice_metadata_1():
    """case 1: test explicit electron metadata always wins"""
    import covalent as ct

    electron_bash_dep = ct.DepsBash(["yum install rustc"])
    lattice_bash_dep = ct.DepsBash(["yum install kernel"])
    ft_before = ct.fs.FileTransfer("/home/ubuntu/src_file", "/home/ubuntu/dest_file")

    # Construct tasks as "electrons"
    @ct.electron(executor="electron_executor", deps_bash=electron_bash_dep, files=[ft_before])
    def task(x):
        return x

    # Construct a workflow of tasks
    @ct.lattice(executor="awslambda", deps_bash=lattice_bash_dep)
    def hello_world(x):
        """This is a basic hello world dispatch"""
        return task(x)

    # Dispatch the workflow
    hello_world.build_graph(1)

    data = hello_world.transport_graph.serialize_to_json()
    data = json.loads(data)

    for node_data in data["nodes"]:
        if node_data["name"].startswith(postprocess_prefix):
            assert node_data["metadata"]["executor"] == get_default_executor()
        elif "parameter" not in node_data["name"]:
            assert node_data["metadata"]["executor"] == "electron_executor"
            assert node_data["metadata"]["deps"]["bash"] == electron_bash_dep.to_dict()
            assert len(node_data["metadata"]["call_before"]) == 2
            assert len(node_data["metadata"]["call_after"]) == 0


def test_electrons_get_lattice_metadata_2():
    """case 2: electron with unset metadata inherits lattice metadata"""
    import covalent as ct

    electron_bash_dep = ct.DepsBash(["yum install rustc"])
    lattice_bash_dep = ct.DepsBash(["yum install kernel"])
    ft_after = ct.fs.FileTransfer(
        "/home/ubuntu/src_file", "/home/ubuntu/dest_file", order=ct.fs.Order.AFTER
    )

    # Construct tasks as "electrons"
    @ct.electron(files=[ft_after])
    def task(x):
        return x

    # Construct a workflow of tasks
    @ct.lattice(executor="lattice_executor", deps_bash=lattice_bash_dep)
    def hello_world(x):
        """This is a basic hello world dispatch"""
        return task(x)

    # Dispatch the workflow
    hello_world.build_graph(1)

    data = hello_world.transport_graph.serialize_to_json()
    data = json.loads(data)

    for node_data in data["nodes"]:
        if node_data["name"].startswith(postprocess_prefix):
            assert node_data["metadata"]["executor"] == get_default_executor()
        elif "parameter" not in node_data["name"]:
            assert node_data["metadata"]["executor"] == "lattice_executor"
            assert node_data["metadata"]["deps"]["bash"] == lattice_bash_dep.to_dict()
            assert len(node_data["metadata"]["call_before"]) == 1
            assert len(node_data["metadata"]["call_after"]) == 1


def test_electrons_get_lattice_metadata_3():
    """case 3: check that default metadata applies if both electron
    and lattice metadata are unset"""

    from dataclasses import asdict

    import covalent as ct
    from covalent._shared_files.defaults import DefaultMetadataValues

    DEFAULT_METADATA_VALUES = asdict(DefaultMetadataValues())
    electron_bash_dep = ct.DepsBash(["yum install rustc"])
    lattice_bash_dep = ct.DepsBash(["yum install kernel"])

    # Construct tasks as "electrons"
    @ct.electron
    def task(x):
        return x

    # Construct a workflow of tasks
    @ct.lattice
    def hello_world(x):
        """This is a basic hello world dispatch"""
        return task(x)

    # Dispatch the workflow
    hello_world.build_graph(1)

    node_meta = hello_world.transport_graph.get_node_value(0, "metadata")
    node_meta["executor"] == DEFAULT_METADATA_VALUES["executor"]
