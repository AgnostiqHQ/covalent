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

from datetime import timezone

from sqlalchemy.sql import func

from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.utils.file_handle import FileHandler
from covalent_ui.api.v1.utils.file_name import FileName


class Electrons:
    """Electron data access layer"""

    def __init__(self, db_con) -> None:
        self.db_con = db_con

    def get_electrons_id(self, dispatch_id, electron_id) -> Electron:
        """
        Read electron table by electron id
        Args:
            electron_id: Refers to the electron's PK
        Return:
            Electron with PK as electron_id
        """
        data = (
            self.db_con.query(
                Electron.id,
                Electron.transport_graph_node_id,
                Electron.parent_lattice_id,
                Electron.type,
                Electron.storage_path,
                Electron.function_filename,
                Electron.function_string_filename,
                Electron.executor,
                Electron.executor_data_filename,
                Electron.results_filename,
                Electron.value_filename,
                Electron.stdout_filename,
                Electron.deps_filename,
                Electron.call_before_filename,
                Electron.call_after_filename,
                Electron.stderr_filename,
                Electron.info_filename,
                Electron.name,
                Electron.status,
                func.datetime(Electron.started_at, "localtime").label("started_at"),
                func.datetime(Electron.completed_at, "localtime").label("completed_at"),
                (
                    (
                        func.strftime(
                            "%s",
                            func.IFNULL(Electron.completed_at, func.datetime.now(timezone.utc)),
                        )
                        - func.strftime("%s", Electron.started_at)
                    )
                    * 1000
                ).label("runtime"),
            )
            .join(Lattice, Lattice.id == Electron.parent_lattice_id)
            .filter(
                Lattice.dispatch_id == str(dispatch_id),
                Electron.transport_graph_node_id == electron_id,
            )
            .first()
        )
        return data

    def read_file(self, electron_id, file_module) -> str:
        """
        File read based on electron id and file module
        Args:
            electron_id: Refers to the electron's PK
            file_module: Refers to file module present from electron
        Return:
            file data as str
        """
        data = (
            self.db_con.query(Electron)
            .filter(Electron.id == electron_id, Electron.electron_id is None)
            .first()
        )
        electron = data[0]
        if file_module == FileName.RESULTS.value:
            file_handler = FileHandler(
                path=electron.storage_path, file_name=electron.results_filename
            )
            return file_handler.read()
        return None
