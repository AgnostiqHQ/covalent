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

"""Unit tests for the defaults module"""

import os
from unittest import mock

import dask.system as dask_system
import pytest


@pytest.fixture
def env_vars():
    return {
        "HOME": "test_home",
        "LOGLEVEL": "TEST_LOG_LEVEL",
        "COVALENT_LOG_TO_FILE": "test_log",
        "COVALENT_EXECUTOR_DIR": "test_exec_dir",
        "COVALENT_DISPATCHER_ADDR": "test_dispatcher_addr",
        "COVALENT_SVC_PORT": "0000",
        "COVALENT_SERVER_IFACE_ANY": "test_server_iface",
        "COVALENT_DEV_PORT": "1111",
        "COVALENT_RESULTS_DIR": "test_results_dir",
    }


def test_get_default_sdk_config(env_vars):
    """Tests that the default SDK configuration is as expected"""

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import get_default_sdk_config

        received_config = get_default_sdk_config()

        assert received_config["config_file"] == "test_home/.config/covalent/covalent.conf"
        assert received_config["log_dir"] == "test_home/.cache/covalent"
        assert received_config["log_level"] == "test_log_level"
        assert received_config["enable_logging"] == "test_log"
        assert received_config["executor_dir"] == "test_exec_dir"
        assert received_config["no_cluster"] == "false"


def test_get_default_server_config(env_vars):
    """Tests that the default server configuration is as expected"""

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import get_default_server_config

        received_config = get_default_server_config()

        assert received_config["address"] == "test_dispatcher_addr"
        assert received_config["port"] == 0000


def test_get_default_service_config(env_vars):
    """Tests that the default service configuration is as expected"""

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import get_default_service_config

        received_config = get_default_service_config()

        assert received_config["address"] == "0.0.0.0"
        assert received_config["port"] == 0000
        assert received_config["dev_port"] == 1111
        assert received_config["results_dir"] == "test_results_dir"
        assert received_config["cache_dir"] == "test_home/.cache/covalent"
        assert received_config["log_dir"] == "test_home/.cache/covalent"
        assert received_config["db_path"] == "test_home/.local/share/covalent/dispatcher_db.sqlite"


def test_get_default_dask_config(env_vars):
    """Tests that the default dask configuration is as expected"""

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import get_default_dask_config

        received_config = get_default_dask_config()

        assert received_config["cache_dir"] == "test_home/.cache/covalent"
        assert received_config["log_dir"] == "test_home/.cache/covalent"
        assert received_config["mem_per_worker"] == "auto"
        assert received_config["threads_per_worker"] == 1
        assert received_config["num_workers"] == dask_system.CPU_COUNT


def test_get_default_workflow_data_config(env_vars):
    """Tests that the default workflow data configuration is as expected"""

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import get_default_workflow_data_config

        received_config = get_default_workflow_data_config()

        assert received_config["storage_type"] == "local"
        assert received_config["base_dir"] == "test_home/.local/share/covalent/workflow_data"


def test_get_default_executor():
    """Tests whether the default executor is set as expected"""

    with mock.patch("covalent._shared_files.config.get_config", return_value="true"):
        from covalent._shared_files.defaults import get_default_executor

        assert get_default_executor() == "local"

    with mock.patch("covalent._shared_files.config.get_config", return_value="false"):
        from covalent._shared_files.defaults import get_default_executor

        assert get_default_executor() == "dask"


def test_get_default_config_path(env_vars):
    """
    Tests that the default configuration path is as expected
    depending on whether the client or the server is accessing it
    """

    with mock.patch.dict(os.environ, env_vars, clear=True):
        from covalent._shared_files.defaults import CMType, get_default_config_path

        assert get_default_config_path(CMType.CLIENT) == "test_home/.config/covalent/covalent.conf"
        assert (
            get_default_config_path(CMType.SERVER) == "test_home/.config/covalent/covalentd.conf"
        )
