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

from covalent._shared_files.config import get_config

log_level = get_config("sdk.log_level").upper()
log_to_file = get_config("sdk.enable_logging").upper() == "TRUE"


def log_config():
    """
    Get Log configurations
    Return:
        Log configuration with respect to settings
    """
    log = log_level if log_to_file else None

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
