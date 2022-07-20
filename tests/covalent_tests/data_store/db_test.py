#!/usr/bin/env python

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

import datetime
from os import path
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from pytest_mock import MockerFixture
from sqlalchemy import select

import alembic
from alembic.config import Config
from covalent._data_store import models
from covalent._data_store.datastore import DataStore, DevDataStore
from covalent._shared_files.config import get_config

from .fixtures import workflow_fixture


@pytest.fixture
def db():
    """Instantiate and return an in-memory database."""

    return DataStore(
        db_URL="sqlite+pysqlite:///:memory:",
        initialize_db=True,
    )


def test_db_path(db: DataStore, tmp_path: Path):
    db_dir_path = tmp_path / "db_dir"
    db_dir_path.mkdir()
    db_path = db_dir_path / "my_db.sqlite"

    db_url = f"sqlite+pysqlite:///{str(db_path.resolve())}"

    db = DataStore(db_URL=db_url, initialize_db=True)
    assert db.db_URL == db_url


def test_default_db_path(db: DataStore, tmp_path: Path, mocker):

    DB_PATH = "/tmp/my_db.sqlite"

    mocker.patch("sqlalchemy.create_engine")
    mocker.patch("sqlalchemy.orm.sessionmaker")
    mocker.patch("covalent._data_store.datastore.get_config", return_value=DB_PATH)

    db_url = f"sqlite+pysqlite:///{DB_PATH}"

    assert DataStore().db_URL == db_url


def test_default_db_dev_path(db: DataStore, tmp_path: Path, mocker):

    DB_PATH = "/tmp/my_db.sqlite"
    DB_DEV_PATH = "/tmp/my_db_dev.sqlite"

    mocker.patch("sqlalchemy.create_engine")
    mocker.patch("sqlalchemy.orm.sessionmaker")
    mocker.patch("covalent._data_store.datastore.get_config", return_value=DB_PATH)

    db_dev_url = f"sqlite+pysqlite:///{DB_DEV_PATH}"

    assert DevDataStore().db_URL == db_dev_url


def test_run_migrations(db: DataStore, mocker):

    alembic_command_mock = Mock()
    alembic_config_mock = MagicMock()

    def alembic_config_init(self, provided_path):
        # ensure provided path matches project root / alembic.ini
        assert provided_path == Path(path.join(__file__, "./../../../../alembic.ini")).resolve()

    mocker.patch.object(Config, "__init__", alembic_config_init)
    mocker.patch("covalent._data_store.datastore.Config", return_value=alembic_config_mock)
    mocker.patch("covalent._data_store.datastore.command", return_value=alembic_command_mock)

    db.run_migrations()


@pytest.mark.usefixtures("workflow_fixture")
def test_insertion(db: DataStore, workflow_fixture):
    electron_dependency = workflow_fixture["electron_dependency"][0]
    with db.session() as session:
        session.add(electron_dependency)
        session.commit()
    with db.session() as session:
        statement = select(models.ElectronDependency)
        results = session.execute(statement).all()
        assert len(results) == 1
