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

from contextlib import contextmanager
from os import path
from pathlib import Path
from typing import BinaryIO, Dict, Generator, List, Optional, Union

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config

from .._shared_files.config import get_config
from . import models
from .storage_backends import LocalStorageBackend, StorageBackend

default_backend_map = {"local": LocalStorageBackend(base_dir=get_config("workflow_data.base_dir"))}


class DataStore:
    def __init__(
        self,
        db_URL: Optional[str] = None,
        storage_backend_map: Dict[str, StorageBackend] = default_backend_map,
        initialize_db: bool = False,
        **kwargs,
    ):
        if db_URL:
            self.db_URL = db_URL
        else:
            self.db_URL = "sqlite+pysqlite:///" + get_config("workflow_data.db_path")

        self.storage_backend_map = storage_backend_map
        self.engine = create_engine(self.db_URL, **kwargs)
        self.Session = sessionmaker(self.engine)

        # flag should only be used in pytest - tables should be generated using migrations
        if initialize_db:
            models.Base.metadata.create_all(self.engine)

    def run_migrations(self):

        alembic_ini_path = Path(path.join(__file__, "./../../../alembic.ini")).resolve()
        alembic_config = Config(alembic_ini_path)
        alembic_config.attributes["configure_logger"] = False
        alembic_config.set_main_option("sqlalchemy.url", self.db_URL)
        command.upgrade(alembic_config, "head")

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        with self.Session.begin() as session:
            yield session


class DevDataStore(DataStore):
    def __init__(
        self,
        db_URL: Optional[str] = None,
        initialize_db: bool = False,
        storage_backend_map: Dict[str, StorageBackend] = default_backend_map,
        **kwargs,
    ):
        if not db_URL:
            db_path = get_config("user_interface.dispatch_db")
            sqlite = ".sqlite"
            db_URL = f"sqlite+pysqlite:///{db_path.split(sqlite)[0]}_dev{sqlite}"
        super().__init__(db_URL, storage_backend_map, initialize_db, **kwargs)


class DataStoreSession:
    def __init__(self, session: Session, metadata={}):
        self.db_session = session
        self.metadata = metadata
        self.pending_uploads = []
        self.pending_deletes = []

    def queue_upload(self, data: BinaryIO, storage_type: str, storage_path: str, file_name: str):
        self.pending_uploads.append((data, storage_type, storage_path, file_name))

    def queue_delete(self, storage_type: str, storage_path: str, file_name: str):
        self.pending_deletes.append((storage_type, storage_path, file_name))


class DataStoreNotInitializedError(Exception):
    """Exception raised when a database action is attempted before the database is initialized."""

    def __init__(self, message="Database is not initialized."):
        self.message = message
        super().__init__(self.message)


# we can switch this to any class instance that has a db_URL property that points to the db
# which we want to run migrations against - this command also creates the db without tables
# via create_engine()
workflow_db = DevDataStore(echo=True)
