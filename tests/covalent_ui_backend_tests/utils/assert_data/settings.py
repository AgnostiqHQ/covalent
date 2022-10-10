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

"""Settings data"""

import os


def seed_settings_data():
    """Mock db assert settings data"""
    config_path = os.environ.get("COVALENT_CONFIG_DIR")
    log_dir = os.environ.get("COVALENT_LOGDIR")
    executor_dir = os.environ.get("COVALENT_EXECUTOR_DIR")
    return {
        "test_settings": {
            "api_path": "/api/v1/settings",
            "case1": {
                "status_code": 200,
            },
            "case2": {
                "status_code": 200,
                "request_body": {
                    "client": {
                        "sdk": {
                            "config_file": config_path,
                            "log_dir": log_dir,
                            "log_level": "info",
                            "enable_logging": "true",
                            "executor_dir": executor_dir,
                            "no_cluster": "true",
                        }
                    }
                },
                "request_params": {"override_existing": False},
                "response_data": {"data": "settings updated successfully"},
            },
        },
    }
