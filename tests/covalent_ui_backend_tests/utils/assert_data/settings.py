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

"""Settings mock data"""


from .config_data import BASE_DIR, CONFIG_PATH, EXECUTOR_DIR, LOG_DIR


def seed_settings_data():
    """Mock db assert settings data"""

    messages = {"update": "settings updated successfully"}
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
                            "config_file": CONFIG_PATH,
                            "log_dir": LOG_DIR,
                            "log_level": "info",
                            "enable_logging": "true",
                            "executor_dir": EXECUTOR_DIR,
                            "no_cluster": "true",
                        }
                    }
                },
                "request_params": {"override_existing": False},
                "response_data": {"data": messages["update"]},
            },
            "case3": {
                "status_code": 400,
                "request_body": {
                    "client": {
                        "": {
                            "config_file": CONFIG_PATH,
                            "log_dir": LOG_DIR,
                            "log_level": "info",
                            "enable_logging": "true",
                            "executor_dir": EXECUTOR_DIR,
                            "no_cluster": "true",
                        }
                    }
                },
                "request_params": {"override_existing": True},
                "response_data": {"data": messages["update"]},
            },
            "case4": {
                "status_code": 400,
                "request_body": {
                    "client": {
                        "sdk": {
                            "config_file": CONFIG_PATH,
                            "log_dir": LOG_DIR,
                            "log_level": "info",
                            "enable_logging": "true",
                            "executor_dir": EXECUTOR_DIR,
                            "no_cluster": "true",
                        },
                    },
                    "workflow_data": {"storage_type": "local", "base_dir": BASE_DIR},
                },
                "request_params": {"override_existing": True},
                "response_data": {"data": messages["update"]},
            },
        },
    }
