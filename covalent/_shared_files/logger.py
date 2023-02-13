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

"""Module for logging errors, warnings, and debug statements."""

import logging
import os
import sys
import time

from .config import get_config

logging.Formatter.converter = time.gmtime

app_log = logging.getLogger(__name__)

log_level = get_config("sdk.log_level").upper()
app_log.setLevel(log_level)

# Set the format
stream_formatter = logging.Formatter(
    "[%(asctime)s] " + "[%(levelname)s] " + "%(filename)s: " + "Line "
    "%(lineno)s in %(funcName)s: " + "%(message)s"
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(log_level)
stream_handler.setFormatter(stream_formatter)
stream_handler.stream = sys.stdout

app_log.addHandler(stream_handler)
app_log.propagate = False

# Show stack traces
log_stack_info = os.environ.get("LOGSTACK", "TRUE").upper() == "TRUE"
