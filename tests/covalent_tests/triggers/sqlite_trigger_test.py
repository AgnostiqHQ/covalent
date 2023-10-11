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


from sqlite3 import OperationalError

import pytest

from covalent.triggers.sqlite_trigger import SQLiteTrigger


@pytest.fixture
def sqlite_trigger():
    """
    Fixture to obtain a sample SQLiteTrigger instance for testing
    """

    db_path = "test_db_path"
    table_name = "test_table_name"
    poll_interval = 1
    where_clauses = ["id > 2", "status = pending"]
    trigger_after_n = 1
    return SQLiteTrigger(db_path, table_name, poll_interval, where_clauses, trigger_after_n)


def test_sqlite_trigger_init(sqlite_trigger):
    """
    Testing whether SQLiteTrigger initializes as expected
    """

    assert sqlite_trigger.db_path == "test_db_path"
    assert sqlite_trigger.table_name == "test_table_name"
    assert sqlite_trigger.poll_interval == 1
    assert sqlite_trigger.where_clauses == ["id > 2", "status = pending"]
    assert sqlite_trigger.trigger_after_n == 1


@pytest.mark.parametrize(
    "where_clauses",
    [
        ["id > 2", "status = pending"],
        None,
    ],
)
def test_sqlite_trigger_observe(mocker, where_clauses, sqlite_trigger):
    """
    Test the observe method of SQLiteTrigger
    """

    sqlite_trigger.where_clauses = where_clauses
    sqlite_trigger.trigger = mocker.MagicMock()

    mock_sqlite = mocker.patch("covalent.triggers.sqlite_trigger.sqlite3")
    mock_event = mocker.patch("covalent.triggers.sqlite_trigger.Event")

    mock_sleep = mocker.patch("covalent.triggers.sqlite_trigger.time.sleep")

    mock_event.return_value.is_set.side_effect = [False, True]

    sqlite_trigger.observe()

    mock_sqlite.connect.assert_called_once_with("test_db_path")
    mock_sqlite.connect.return_value.row_factory = mock_sqlite.Row
    mock_sqlite.connect.return_value.cursor.assert_called_once()

    mock_event.assert_called_once()

    sql_poll_cmd = "SELECT * FROM test_table_name"
    if where_clauses:
        sql_poll_cmd += " WHERE "
        sql_poll_cmd += " AND ".join(list(where_clauses))

    mock_sqlite.connect.return_value.cursor.return_value.execute.assert_called_once_with(
        sql_poll_cmd
    )

    mock_sqlite.connect.return_value.cursor.return_value.fetchall.assert_called_once()

    sqlite_trigger.trigger.assert_called_once()
    mock_sleep.assert_called_once_with(1)

    mock_sqlite.connect.return_value.cursor.return_value.close.assert_called_once()
    mock_sqlite.connect.return_value.close.assert_called_once()


def test_sqlite_trigger_exception(mocker, sqlite_trigger):
    """
    Test the observe method of SQLiteTrigger when an OperationalError is raised
    """

    sqlite_trigger.trigger = mocker.MagicMock()

    mock_connect = mocker.patch("covalent.triggers.sqlite_trigger.sqlite3.connect")
    mocker.patch("covalent.triggers.sqlite_trigger.sqlite3.Row")
    mock_event = mocker.patch("covalent.triggers.sqlite_trigger.Event")

    mock_sleep = mocker.patch("covalent.triggers.sqlite_trigger.time.sleep")

    mock_event.return_value.is_set.side_effect = [False, True]

    mock_connect.return_value.cursor.return_value.execute.side_effect = OperationalError

    sqlite_trigger.observe()

    mock_sleep.assert_called_once_with(1)


def test_sqlite_trigger_stop(mocker, sqlite_trigger):
    """
    Test the stop method of SQLiteTrigger
    """

    mock_stop_flag = mocker.MagicMock()
    sqlite_trigger.stop_flag = mock_stop_flag

    sqlite_trigger.stop()

    mock_stop_flag.set.assert_called_once()
