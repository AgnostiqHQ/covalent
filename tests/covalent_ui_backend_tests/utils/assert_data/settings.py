"""Settings data"""


def seed_settings_data():
    """Mock db assert settings data"""
    config_path = "/home/manjunathpoilath/.config/covalent/covalent.conf"
    log_dir = "/home/manjunathpoilath/.cache/covalent"
    executor_dir = "/home/manjunathpoilath/.config/covalent/executor_plugins"
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
