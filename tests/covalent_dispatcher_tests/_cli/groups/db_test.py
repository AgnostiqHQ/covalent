from unittest.mock import Mock

from click.testing import CliRunner

from covalent._data_store.datastore import DataStore
from covalent_dispatcher._cli.groups.db import MIGRATION_WARNING_MSG, migrate


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
