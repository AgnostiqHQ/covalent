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
from typing import Optional, Tuple, Union

import sqlalchemy
from app.core.config import settings
from sqlalchemy_utils import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_database,
    database_exists,
)


class Database:
    def __init__(
        self,
        database_backend: str = "sqlite",
        db_name: str = None,
        db_endpoint: str = None,
        db_port: int = 3306,
        db_user: str = "admin",
        db_password: str = None,
    ):

        self.database_backend = database_backend
        self.db_name = db_name if db_name else settings.WORKFLOW_DB_NAME

        if self.database_backend == "sqlite":
            engine = sqlalchemy.create_engine(f"sqlite:///{self.db_name}")
        elif self.database_backend == "mysql":
            self.db_endpoint = db_endpoint
            self.db_port = db_port
            self.db_user = db_user
            self.db_password = db_password

            engine = sqlalchemy.create_engine(
                f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_endpoint}:{self.db_port}/{self.db_name}"
            )

        if not database_exists(engine.url):
            create_database(engine.url)

        if not engine.pymysql.has_table(engine, "dispatch"):
            metadata = MetaData(engine)
            dispatch_table = Table(
                "dispatch",
                metadata,
                Column("id", String, primary_key=True),
                Column("parent_id", String),
                Column("name", String),
                Column("status", String),
                # TODO: Continue here
            )

        # sql = (
        #    "CREATE TABLE IF NOT EXISTS results ("
        #    "dispatch_id text NOT NULL, "
        #    "filename text NOT NULL, "
        #    "path text NOT NULL, "
        #    "PRIMARY KEY (dispatch_id))"
        # )

        # self.logger = logging.getLogger(__name__)
        # self.logger.info("Executing SQL command.")
        # self.logger.info(sql)

        # cur.execute(sql)
        # con.commit()
        # con.close()

    def value(self, sql: str, key: str = None) -> Optional[Tuple[Union[bool, str]]]:
        import sqlite3

        con = sqlite3.connect(self.sqlite_db_name)
        cur = con.cursor()
        self.logger.info("Executing SQL command.")
        self.logger.info(sql)
        value = (False,)
        if key:
            self.logger.info("Searching for key " + key)
            cur.execute(sql, (key,))
            value = cur.fetchone()
        else:
            cur.execute(sql)
            value = (True,)
        con.commit()
        con.close()
        return value
