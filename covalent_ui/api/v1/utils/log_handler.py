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

from covalent._shared_files.config import get_config

log_level = get_config("sdk.log_level").upper()
log_to_file = get_config("sdk.enable_logging").upper() == "TRUE"

if log_to_file:
    log = log_level
else:
    log = None


def log_config():
    """
    Get Log configurations
    Return:
        Log configuration with respect to settings
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(asctime)s,%(msecs)03d] [%(levelname)s] %(message)s",
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(asctime)s,%(msecs)03d] [%(levelname)s] %(message)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn.error": {"level": log, "handlers": ["default"], "propogate": False},
            "uvicorn.access": {"level": log, "handlers": ["access"], "propagate": "no"},
        },
    }
