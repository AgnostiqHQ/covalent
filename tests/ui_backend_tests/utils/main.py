import os

import covalent_ui.api.v1.database.config as config
from covalent_ui.app import fastapi_app


@fastapi_app.on_event("startup")
def init():
    mock_path = (
        "sqlite+pysqlite:///" + os.environ["HOME"] + "/.local/share/covalent/mock_db.sqlite"
    )
    config.db.init_db(db_path=mock_path)
