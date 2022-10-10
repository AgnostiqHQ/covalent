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

import os
import shutil

import covalent_ui.api.v1.database.config as config
from covalent_ui.app import fastapi_app
from tests.covalent_ui_backend_tests.utils.seed_script import log_output_data, seed, seed_files

mock_db_path = os.path.join("tests/covalent_ui_backend_tests/utils/data", "mock_db.sqlite")


@fastapi_app.on_event("startup")
def init():
    mock_path = f"sqlite+pysqlite:///{mock_db_path}"
    config.db.init_db(db_path=mock_path)
    seed(config.db.engine)
    seed_files()


@fastapi_app.on_event("shutdown")
def de_init():
    os.remove(mock_db_path)
    print("remove mock file", mock_db_path)
    shutil.rmtree(log_output_data["lattice_files"]["path"])
    shutil.rmtree(log_output_data["log_files"]["path"])
