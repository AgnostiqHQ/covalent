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

"""Unit tests for the AsyncNodeInfoManager class"""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

import covalent as ct
from covalent._results_manager.nodeinfomanager import AsyncNodeInfoManager
from covalent._results_manager.result import Result
from covalent._workflow.lattice import Lattice


@pytest.mark.asyncio
async def test_get_file_handle():
    @ct.electron
    def task(x):
        return x

    @ct.lattice
    def workflow(x):
        return task(x)

    workflow.build_graph(5)

    received_lattice = Lattice.deserialize_from_json(workflow.serialize_to_json())

    result_object = Result(received_lattice, "/tmp", "asdf")

    result_object._initialize_nodes()
    tg = result_object.lattice.transport_graph
    nm = AsyncNodeInfoManager(tg, "/tmp", "asdf", 0)

    f = NamedTemporaryFile(delete=True)

    monitored_file = f.name

    f.close()

    async with nm.get_file_handle(monitored_file) as f:
        await f.write("Hello\n")

    node_info = tg.get_node_value(0, "info")
    datastore_uri = node_info[monitored_file]
    metadata_uri = datastore_uri + ".meta"

    with open(datastore_uri, "r") as f:
        assert f.read() == "Hello\n"

    with open(metadata_uri, "r") as f:
        assert f.readline() == monitored_file

    os.unlink(datastore_uri)
    os.unlink(metadata_uri)
