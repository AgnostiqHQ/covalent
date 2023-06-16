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
from os import environ, path
from pathlib import Path
from typing import Generator, Optional

from alembic import command
from alembic.config import Config
from alembic.environment import EnvironmentContext
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists

from covalent._shared_files.config import get_config

from . import models

DEBUG_DB = environ.get("COVALENT_DEBUG_DB") == "1"


class DataStore:
    def __init__(
        self,
        db_URL: Optional[str] = None,
        initialize_db: bool = False,
        **kwargs,
    ):
        if db_URL:
            self.db_URL = db_URL
        else:
            self.db_URL = "sqlite+pysqlite:///" + get_config("dispatcher.db_path")

        self.engine = create_engine(self.db_URL, **kwargs)
        if not database_exists(self.engine.url):
            create_database(self.engine.url)
        self.Session = sessionmaker(self.engine)

        # flag should only be used in pytest - tables should be generated using migrations
        if initialize_db:
            models.Base.metadata.create_all(self.engine)

    @staticmethod
    def factory():
        return DataStore(db_URL=environ.get("COVALENT_DATABASE_URL"), echo=DEBUG_DB)

    def get_alembic_config(self, logging_enabled: bool = True):
        alembic_ini_path = Path(path.join(__file__, "./../../../covalent_migrations/alembic.ini"))
        migrations_folder = alembic_ini_path / Path("..")
        alembic_config = Config(str(alembic_ini_path.resolve()))
        alembic_config.set_main_option("script_location", str(migrations_folder.resolve()))
        alembic_config.attributes["configure_logger"] = logging_enabled
        alembic_config.set_main_option("sqlalchemy.url", self.db_URL)
        return alembic_config

    def run_migrations(self, logging_enabled: bool = True):
        alembic_config = self.get_alembic_config(logging_enabled=logging_enabled)
        command.upgrade(alembic_config, "head")

    def current_revision(self):
        alembic_config = self.get_alembic_config(logging_enabled=False)
        script = ScriptDirectory.from_config(alembic_config)
        with EnvironmentContext(alembic_config, script) as env_ctx:
            migration_ctx = MigrationContext.configure(
                self.engine.connect(), environment_context=env_ctx
            )
            current_rev = migration_ctx.get_current_revision()
            return current_rev

    def current_head(self):
        alembic_config = self.get_alembic_config(logging_enabled=False)
        script = ScriptDirectory.from_config(alembic_config)
        current_head = script.get_current_head()
        return current_head

    @property
    def is_migration_pending(self):
        return self.current_head() != self.current_revision()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        with self.Session.begin() as session:
            yield session


workflow_db = DataStore.factory()
