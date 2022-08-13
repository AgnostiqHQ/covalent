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

import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import aiofiles

from .._workflow.transport import _TransportGraph


class AsyncNodeInfoManager:
    """Intermediatry between monitored files and datastore"""

    def __init__(self, tg: _TransportGraph, results_dir: str, dispatch_id: str, node_id: int):
        self.tg = tg
        self.dispatch_id = dispatch_id
        self.node_id = node_id

        # FIX: This should really be defined by the server-side data store,
        # not the lattice-level results_dir
        self.results_dir = results_dir

        self.path_map = {}

    def update_node_info(self, monitored_file_path, datastore_uri):
        node_info: dict = self.tg.get_node_value(self.node_id, "info")
        node_info[monitored_file_path] = str(datastore_uri)

        # Marks the node as dirty so that it will be included with
        # the next datastore write
        self.tg.set_node_value(self.node_id, "info", node_info)

    @asynccontextmanager
    async def get_file_handle(self, monitored_file_path: str):
        node_path = Path(self.results_dir) / self.dispatch_id / f"node_{self.node_id}"
        monitored_files_dir = Path(self.results_dir) / node_path / Path("monitored_files")
        if not monitored_files_dir.exists():
            monitored_files_dir.mkdir(parents=True)

        object_name = str(uuid.uuid4())
        metadata_name = object_name + ".meta"

        datastore_uri = monitored_files_dir / object_name
        metadata_uri = monitored_files_dir / metadata_name
        self.update_node_info(monitored_file_path, datastore_uri)

        async with aiofiles.open(metadata_uri, "w") as f:
            await f.write(monitored_file_path)

        async with aiofiles.open(datastore_uri, "a") as f:
            yield f
