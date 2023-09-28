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
