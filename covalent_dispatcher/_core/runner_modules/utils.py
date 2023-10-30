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


def get_executor(node_id, selected_executor, loop=None, pool=None) -> AsyncBaseExecutor:
    # Instantiate the executor from JSON

    short_name, object_dict = selected_executor

    app_log.debug(f"Running task {node_id} using executor {short_name}, {object_dict}")

    # the executor is determined during scheduling and provided in the execution metadata
    executor = _executor_manager.get_executor(short_name)
    executor.from_dict(object_dict)
    executor._init_runtime(loop=loop, cancel_pool=pool)

    return executor
