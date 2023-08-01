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

"""Config data"""

import os

from covalent._shared_files.config import get_config

VALID_DISPATCH_ID = "78525234-72ec-42dc-94a0-f4751707f9cd"
INVALID_DISPATCH_ID = "78525234-72ec-42dc-94a0-f4751707f9ef"
VALID_NODE_ID = 0
INVALID_NODE_ID = 8
CONFIG_PATH = os.environ.get("COVALENT_CONFIG_DIR")
LOG_DIR = os.environ.get("COVALENT_LOGDIR")
EXECUTOR_DIR = os.environ.get("COVALENT_EXECUTOR_DIR")
BASE_DIR = os.environ.get("COVALENT_DATA_DIR")
LOG_FORMAT = "[%(asctime)s,%(msecs)03d] [%(levelname)s] %(message)s"
LOG_LEVEL = get_config("sdk.log_level").upper()
LOG_TO_FILE = get_config("sdk.enable_logging").upper() == "TRUE"
