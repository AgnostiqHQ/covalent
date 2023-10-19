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

import os
import shutil
from pathlib import Path

import covalent_ui.api.v1.database.config as config

from ..utils.seed_script import log_output_data, seed, seed_files

mock_db_path = str(Path(__file__).parent.parent.absolute()) + "/utils/data/mock_db.sqlite"
mock_path = f"sqlite+pysqlite:///{mock_db_path}"


def startup_event():
    config.db.init_db(db_path=mock_path)
    seed(config.db.engine)
    seed_files()


def shutdown_event():
    os.remove(mock_db_path)
    shutil.rmtree(log_output_data["lattice_files"]["path"])
    shutil.rmtree(log_output_data["log_files"]["path"])
