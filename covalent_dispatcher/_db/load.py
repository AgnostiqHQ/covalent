# Copyright 2023 Agnostiq Inc.
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

"""Functions to load results from the database."""

from typing import Optional

from covalent._results_manager.result import Result
from covalent._shared_files import logger

from .models import Lattice

app_log = logger.app_log
log_stack_info = logger.log_stack_info


def _result_from(lattice_record: Lattice) -> Result:
    """Re-hydrate result object from the lattice record."""
    pass


def get_result_object_from_storage(
    dispatch_id: str, wait: Optional[bool] = False, status_only: Optional[bool] = False
):
    """Get result object from Database."""
    pass
