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

from covalent_ui.app.api_v0.database.schema.electrons_schema import Electron
from covalent_ui.app.api_v0.utils.file_handle import FileHandler
from covalent_ui.app.api_v0.utils.file_name import FileName


class Electrons:
    """Electron data access layer"""

    def __init__(self, db_con) -> None:
        self.db_con = db_con

    def get_electrons_id(self, electron_id: int) -> Electron:
        """
        Read electron table by electron id
        Args:
            electron_id: Refers to the electron's PK
        Return:
            Electron with PK as electron_id
        """
        return self.db_con.query(Electron).filter(Electron.id == electron_id).first()

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
