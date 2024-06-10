# Copyright 2023 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import sqlalchemy

from covalent.triggers.database_trigger import DatabaseTrigger


@pytest.fixture
def database_trigger():
    """
    Fixture to obtain a sample Database Trigger instance for testing
    """

    db_path = "test_db_path"
    table_name = "test_table_name"
    poll_interval = 1
    where_clauses = ["id > 2", "status = pending"]
    trigger_after_n = 1
    return DatabaseTrigger(db_path, table_name, poll_interval, where_clauses, trigger_after_n)


def test_sqlite_trigger_init(database_trigger):
    """
    Testing whether Database Trigger initializes as expected
    """

    assert database_trigger.db_path == "test_db_path"
    assert database_trigger.table_name == "test_table_name"
    assert database_trigger.poll_interval == 1
    assert database_trigger.where_clauses == ["id > 2", "status = pending"]
    assert database_trigger.trigger_after_n == 1


@pytest.mark.parametrize(
    "where_clauses",
    [
        ["id > 2", "status = pending"],
        None,
    ],
)
def test_database_trigger_observe(mocker, where_clauses, database_trigger):
    """
    Test the observe method of Database Trigger
    """

    database_trigger.where_clauses = where_clauses
    database_trigger.trigger = mocker.MagicMock()

    mock_db_engine = mocker.patch("sqlalchemy.create_engine")
    mock_session = mocker.patch("sqlalchemy.orm.Session")
    mock_event = mocker.patch("covalent.triggers.database_trigger.Event")
    mock_sleep = mocker.patch("covalent.triggers.database_trigger.time.sleep")

    mock_event.return_value.is_set.side_effect = [False, True]
    database_trigger.observe()

    sql_poll_cmd = "SELECT * FROM test_table_name"
    if where_clauses:
        sql_poll_cmd += " WHERE "
        sql_poll_cmd += " AND ".join(list(where_clauses))
    sql_poll_cmd += ";"

    mock_db_engine.assert_called_once_with("test_db_path")
    mock_session.assert_called_once_with(mock_db_engine("test_db_path"))
    mock_event.assert_called_once()
    mock_sql_execute = mock_session.return_value.__enter__.return_value.execute
    mock_sql_execute.assert_called_once_with(sql_poll_cmd)
    mock_sleep.assert_called_once_with(1)


@pytest.mark.skip(
    reason="Not sure what the purpose of this test is since no specific exception is raised or checked for."
)
@pytest.mark.parametrize(
    "where_clauses",
    [
        ["id > 2", "status = COMPLETED"],
        None,
    ],
)
def test_database_trigger_exception(mocker, where_clauses, database_trigger):
    """
    Test the observe method of Database trigger when an OperationalError is raised
    """

    mock_db_engine = mocker.patch("covalent.triggers.database_trigger.create_engine")
    mock_session = mocker.patch("covalent.triggers.database_trigger.Session")
    mock_event = mocker.patch("covalent.triggers.database_trigger.Event")
    mock_sleep = mocker.patch("covalent.triggers.database_trigger.time.sleep")

    mock_event.return_value.is_set.side_effect = [False, True]
    database_trigger.observe()

    sql_poll_cmd = "SELECT * FROM test_table_name"
    if where_clauses:
        sql_poll_cmd += " WHERE "
        sql_poll_cmd += " AND ".join(list(where_clauses))
    sql_poll_cmd += ";"

    mock_db_engine.assert_called_once_with("test_db_path")
    mock_session.assert_called_once_with(mock_db_engine("test_db_path"))
    mock_event.assert_called_once()
    mock_sql_execute = mocker.patch.object(mock_session, "execute", autospec=True)
    mock_sql_execute.assert_called_once_with(sql_poll_cmd)
    mock_sleep.assert_called_once_with(1)


def test_database_trigger_exception_session(mocker, database_trigger):
    """
    Test the observe method of Database trigger when an ArgumentError is raised
    """
    database_trigger.trigger = mocker.MagicMock()
    mock_event = mocker.patch("covalent.triggers.database_trigger.Event")
    mock_event.return_value.is_set.side_effect = [False, True]

    # Call the 'observer' method
    try:
        database_trigger.observe()
    except sqlalchemy.exc.ArgumentError as exc:
        assert str(exc) == "Could not parse SQLAlchemy URL from string 'test_db_path'"


def test_database_trigger_stop(mocker, database_trigger):
    """
    Test the stop method of Database Trigger
    """

    mock_stop_flag = mocker.MagicMock()
    database_trigger.stop_flag = mock_stop_flag

    database_trigger.stop()

    mock_stop_flag.set.assert_called_once()
