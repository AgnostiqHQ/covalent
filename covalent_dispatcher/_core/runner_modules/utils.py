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

"""
Defines the core functionality of the runner
"""


from covalent._shared_files import logger
from covalent._shared_files.config import get_config
from covalent.executor import _executor_manager
from covalent.executor.base import AsyncBaseExecutor

app_log = logger.app_log
log_stack_info = logger.log_stack_info
debug_mode = get_config("sdk.log_level") == "debug"


def get_executor(node_id, selected_executor) -> AsyncBaseExecutor:
    # Instantiate the executor from JSON

    short_name, object_dict = selected_executor

    app_log.debug(f"Running task {node_id} using executor {short_name}, {object_dict}")

    # the executor is determined during scheduling and provided in the execution metadata
    executor = _executor_manager.get_executor(short_name)
    executor.from_dict(object_dict)

    return executor
