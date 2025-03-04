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

import codecs
import pickle
import uuid
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import extract, select
from sqlalchemy.sql import func

from covalent._results_manager.results_manager import get_result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent_dispatcher._core.execution import _get_task_inputs as get_task_inputs
from covalent_ui.api.v1.database.schema.electron import Electron
from covalent_ui.api.v1.database.schema.lattices import Lattice
from covalent_ui.api.v1.utils.file_handle import validate_data

app_log = logger.app_log
RESULTS_DIR = Path(get_config("dispatcher")["results_dir"]).resolve()


class Electrons:
    """Electron data access layer"""

    def __init__(self, db_con) -> None:
        self.db_con = db_con

    def electron_exist(self, electron_id: int) -> bool:
        return self.db_con.execute(
            select(Electron).where(Electron.transport_graph_node_id == electron_id)
        ).fetchone()

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
                Electron.executor_data,
                Electron.results_filename,
                Electron.value_filename,
                Electron.stdout_filename,
                Electron.hooks_filename,
                Electron.stderr_filename,
                Electron.error_filename,
                Electron.name,
                Electron.status,
                Electron.job_id,
                Electron.started_at.label("started_at"),
                Electron.completed_at.label("completed_at"),
                (
                    (
                        func.coalesce(
                            extract("epoch", Electron.completed_at),
                            extract("epoch", func.now()),
                        )
                        - extract("epoch", Electron.started_at)
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

        result = get_result(dispatch_id=str(dispatch_id), wait=False)
        if isinstance(result, JSONResponse) and result.status_code == 404:
            raise HTTPException(status_code=400, detail=result)
        result_object = pickle.loads(codecs.decode(result["result"].encode(), "base64"))
        electron_result = self.get_electrons_id(dispatch_id, electron_id)
        inputs = get_task_inputs(
            node_id=electron_id, node_name=electron_result.name, result_object=result_object
        )
        return validate_data(inputs)
