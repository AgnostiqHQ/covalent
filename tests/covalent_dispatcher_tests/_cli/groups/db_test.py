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
import sys
from unittest.mock import Mock

from click.testing import CliRunner

from covalent_dispatcher._cli.groups.db import MIGRATION_WARNING_MSG, alembic, migrate
from covalent_dispatcher._db.datastore import DataStore


def test_migration_with_warning(mocker):
    """Test the start CLI command invoking migration warning"""
    runner = CliRunner()
    db_mock = Mock()
    db_mock.run_migrations.side_effect = Exception("migration issue")
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    res = runner.invoke(migrate, catch_exceptions=False)
    assert MIGRATION_WARNING_MSG in res.output


def test_migration_success(mocker):
    runner = CliRunner()
    db_mock = Mock()
    mocker.patch.object(DataStore, "factory", lambda: db_mock)
    res = runner.invoke(migrate, catch_exceptions=False)
    db_mock.run_migrations.assert_called_once()


def test_alembic_command_args(mocker):
    runner = CliRunner()
    MOCK_ALEMBIC_ARGS_VALID = "current"
    MOCK_ALEMBIC_ARGS_INVALID = "some alembic command --with-flags -m 'comment'"
    ALEMBIC_ERROR_STDERR = b"alembic: error: invalid..."
    ALEMBIC_ERROR_STDOUT = b"b60c5 (head)"
    popen_mock = mocker.patch.object(sys.modules["covalent_dispatcher._cli.groups.db"], "Popen")
    # test valid alembic args
    popen_mock().communicate.return_value = (ALEMBIC_ERROR_STDOUT, b"")
    res = runner.invoke(alembic, MOCK_ALEMBIC_ARGS_VALID, catch_exceptions=False)
    assert ALEMBIC_ERROR_STDOUT.decode("utf-8") in res.output
    # test invalid alembic args
    popen_mock().communicate.return_value = (b"", ALEMBIC_ERROR_STDERR)
    res = runner.invoke(alembic, MOCK_ALEMBIC_ARGS_INVALID, catch_exceptions=False)
    assert ALEMBIC_ERROR_STDERR.decode("utf-8") in res.output


def test_alembic_not_installed_error(mocker):
    runner = CliRunner()
    MOCK_ALEMBIC_ARGS = "current"
    EXCEPTION_MESSAGE = "[Errno 2] No such file or directory: 'alembic'"
    popen_mock = mocker.patch.object(sys.modules["covalent_dispatcher._cli.groups.db"], "Popen")
    popen_mock.side_effect = FileNotFoundError(EXCEPTION_MESSAGE)
    res = runner.invoke(alembic, MOCK_ALEMBIC_ARGS, catch_exceptions=False)
    assert EXCEPTION_MESSAGE in res.output
    assert res.exit_code == 1
