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
from datetime import timezone

from sqlalchemy.sql import func

from covalent._results_manager.results_manager import get_result
from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.utils.file_handle import validate_data


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

    def get_electron_inputs(self, dispatch_id: uuid.UUID, electron_id: int) -> str:
        """
        Get Electron Inputs
        Args:
            dispatch_id: Dispatch id of lattice/sublattice
            electron_id: Transport graph node id of a electron
        Returns:
            Returns the inputs data from Result object
        """
        from covalent_dispatcher._core.execution import _get_task_inputs as get_task_inputs

        result_object = get_result(dispatch_id=str(dispatch_id), wait=False)

        result = self.get_electrons_id(dispatch_id, electron_id)
        inputs = get_task_inputs(
            node_id=electron_id, node_name=result.name, result_object=result_object
        )
        return validate_data(inputs)
