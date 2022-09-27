/**
 * Copyright 2021 Agnostiq Inc.
 *
 * This file is part of Covalent.
 *
 * Licensed under the GNU Affero General Public License 3.0 (the "License").
 * A copy of the License may be obtained with this software package or at
 *
 *      https://www.gnu.org/licenses/agpl-3.0.en.html
 *
 * Use of this file is prohibited except in compliance with the License. Any
 * modifications or derivative works of this file must retain this copyright
 * notice, and modified files must contain a notice indicating that they have
 * been altered from the originals.
 *
 * Covalent is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
 *
 * Relief from the License may be granted by purchasing a commercial license.
 */

const settingsDemoData = {
    settingsOverview: {
        "client": {
            "sdk": {
                "config_file": "/home/covalent/.config/covalent/covalent.conf",
                "log_dir": "/home/covalent/.cache/covalent",
                "log_level": "info",
                "enable_logging": "true",
                "executor_dir": "/home/covalent/.config/covalent/executor_plugins",
                "no_cluster": "false"
            },
            "server": {
                "address": "localhost",
                "port": 48008
            },
            "executors": {
                "local": {
                    "log_stdout": "stdout.log",
                    "log_stderr": "stderr.log",
                    "cache_dir": "/home/covalent/.cache/covalent"
                },
                "remote_executor": {
                    "poll_freq": 15,
                    "remote_cache": ".cache/covalent",
                    "credentials_file": ""
                },
                "dask": {
                    "log_stdout": "stdout.log",
                    "log_stderr": "stderr.log",
                    "cache_dir": "/home/covalent/.cache/covalent"
                }
            }
        },
        "server": {
            "service": {
                "address": "localhost",
                "port": 48008,
                "dev_port": 49009,
                "results_dir": "results",
                "cache_dir": "/home/covalent/.cache/covalent",
                "log_dir": "/home/covalent/.cache/covalent",
                "db_path": "/home/covalent/.local/share/covalent/dispatcher_db.sqlite"
            },
            "dask": {
                "cache_dir": "/home/covalent/.cache/covalent",
                "log_dir": "/home/covalent/.cache/covalent",
                "mem_per_worker": "auto",
                "threads_per_worker": 1,
                "num_workers": 8,
                "scheduler_address": "tcp://127.0.0.1:44799",
                "dashboard_link": "http://127.0.0.1:8787/status",
                "process_info": "<DaskCluster name='LocalDaskCluster' parent=7333 started>",
                "pid": 7359,
                "admin_host": "127.0.0.1",
                "admin_port": 51681
            },
            "workflow_data": {
                "storage_type": "local",
                "base_dir": "/home/covalent/.local/share/covalent/workflow_data"
            }
        }
    }
}

export default settingsDemoData
