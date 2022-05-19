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

import logging
import os
import re
from typing import Optional, Tuple, Union

import sqlalchemy
from app.core.config import HOME_PATH, settings
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table
from sqlalchemy_utils import create_database, database_exists


class Database:
    def __init__(
        self,
        database_backend: str = None,
        db_name: str = None,
        db_endpoint: str = None,
        db_port: int = None,
        db_user: str = None,
        db_password: str = None,
    ):

        self.database_backend = database_backend or settings.DATABASE_BACKEND
        self.db_name = db_name or settings.DISPATCH_DB_NAME

        self.logger = logging.getLogger(__name__)

        if self.database_backend == "mysql":
            self.db_endpoint = db_endpoint or settings.DISPATCH_DB_ENDPOINT
            self.db_port = db_port or settings.DISPATCH_DB_PORT
            self.db_user = db_user or settings.DISPATCH_DB_USER

        self.connect(db_password or settings.DISPATCH_DB_PASSWORD)

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

        if not sqlalchemy.inspect(self.engine).has_table("workflow"):
            self.create_workflow_table()

    def connect(self, db_password: str = None):
        if self.database_backend == "sqlite":
            abs_db_path = os.path.join(HOME_PATH, "covalent", self.db_name)
            self.engine = sqlalchemy.create_engine(f"sqlite+pysqlite:///{abs_db_path}")
            self.logger.info("Connected to local SQLite database")
        elif self.database_backend == "mysql":
            self.engine = sqlalchemy.create_engine(
                f"mysql+pymysql://{self.db_user}:{db_password}@{self.db_endpoint}:{self.db_port}/{self.db_name}",
                pool_recycle=3600,
            )
            self.logger.info(f"Connected to MySQL database at {self.db_endpoint}")
        else:
            error_str = "Database backend not supported."
            self.logger.error(error_str)
            raise ValueError(error_str)

    def create_workflow_table(self):
        # TODO: Can metadata also be stored as a class variable?
        metadata = MetaData(self.engine)
        workflow_table = Table(
            "workflow",
            metadata,
            Column("id", String(256), primary_key=True),
            Column("results_filename", String(256)),
            Column("results_path", String(256)),
            # TODO: Modify the schema
        )

        metadata.create_all(self.engine)

        self.logger.info("Created workflow table")

    def create_task_table(self, table_name: str):
        name_pattern = re.compile("^[a-zA-Z0-9_]+$")
        if not re.match(name_pattern, table_name):
            raise ValueError("Invalid table name.")

        metadata = MetaData(self.engine)
        task_table = Table(
            table_name,
            metadata,
            Column("id", Integer, primary_key=True),
            # TODO: Decide on the schema later
        )

        metadata.create_all(self.engine)

        self.logger.info(f"Created task table {table_name}")

    def value(self, sql: str) -> str:
        self.logger.info("Executing SQL command.")
        self.logger.info(sql)

        connection = self.engine.connect()
        trans = connection.begin()
        response = connection.execute(sql)
        trans.commit()

        try:
            res = [r for r in response]
        except sqlalchemy.exc.ResourceClosedError:
            res = response.rowcount

        return res
