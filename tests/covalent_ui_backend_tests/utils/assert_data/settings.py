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
