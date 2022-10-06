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
    shutil.rmtree(log_output_data["lattice_files"]["path"])
    shutil.rmtree(log_output_data["log_files"]["path"])
