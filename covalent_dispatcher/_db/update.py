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

import os
from pathlib import Path
from typing import Union

from covalent._results_manager import Result
from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent._workflow.lattice import Lattice
from covalent._workflow.transport import _TransportGraph

from . import upsert

app_log = logger.app_log


def persist(record: Union[Result, Lattice, _TransportGraph], electron_id: int = None) -> None:
    """Save Result object to a DataStore. Changes are queued until
    committed by the caller.

    Args:
        record: The entity to persist in the DB
        electron_id: (hack) DB-generated id for the parent electron
            if the workflow is actually a subworkflow
    """

    _initialize_results_dir(record)
    app_log.debug(f"Persisting {record}")
    upsert.persist_result(record, electron_id)
    app_log.debug("persist complete")


def _initialize_results_dir(result):
    """Create the results directory."""

    result_folder_path = os.path.join(
        os.environ.get("COVALENT_DATA_DIR") or get_config("dispatcher.results_dir"),
        f"{result.dispatch_id}",
    )
    Path(result_folder_path).mkdir(parents=True, exist_ok=True)
