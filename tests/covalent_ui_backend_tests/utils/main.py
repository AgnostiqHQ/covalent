import os

import covalent_ui.api.v1.database.config as config
from covalent_ui.app import fastapi_app
from tests.covalent_ui_backend_tests.utils.seed_script import seed

mock_db_path = os.path.join(os.environ["HOME"], ".local/share/covalent", "mock_db.sqlite")


@fastapi_app.on_event("startup")
def init():
    mock_path = f"sqlite+pysqlite:///{mock_db_path}"
    config.db.init_db(db_path=mock_path)
    seed(config.db.engine)


@fastapi_app.on_event("shutdown")
def de_init():
    os.remove(mock_db_path)
