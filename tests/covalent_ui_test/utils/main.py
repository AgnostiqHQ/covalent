import os

from covalent_ui.api.v1.database.config.db import init_db
from covalent_ui.app import fastapi_app


@fastapi_app.on_event("startup")
def init():
    path = os.chdir("..")
    print(path)
    mock_path = (
        "sqlite+pysqlite:///" + os.environ["HOME"] + "/.local/share/covalent/mock_db.sqlite"
    )
    init_db(db_path=mock_path)
