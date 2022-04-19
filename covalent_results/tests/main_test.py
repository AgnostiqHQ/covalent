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
import os
import pickle
import tempfile
from unittest.mock import patch

from app.core import db

DIRNAME = os.path.dirname(__file__)
FILENAME = os.path.join(DIRNAME, "./_test_assets/result")
MOCK_DISPATCH_ID = "1234"
FS_SERVER_ADDRESS = "localhost:8004"
BASE_URL = FS_SERVER_ADDRESS + "/api/v0/fs"


def file_reader():
    with open(FILENAME, "rb") as f:
        yield from f


def test_get(test_app, monkeypatch):
    async def mock_download(_, filename):
        return b"".join(file_reader())

    def mock_value(_, sql: str, key: str = None):
        return (True,)

    monkeypatch.setattr("app.core.api.DataService.download", mock_download)
    monkeypatch.setattr("app.core.db.Database.value", mock_value)

    response = test_app.get(f"/api/v0/workflow/results/{MOCK_DISPATCH_ID}")

    with open(FILENAME, "rb") as f:
        file_length = f.seek(0, 2)

    assert response.status_code < 400
    assert len(response.content) == file_length


def test_post(test_app, monkeypatch):
    mock_object_name = "mockresult"

    async def mock_upload(_, file):
        return {"filename": FILENAME, "path": DIRNAME}

    def mock_value(_, sql: str, key: str = None):
        return (True,)

    monkeypatch.setattr("app.core.api.DataService.upload", mock_upload)
    monkeypatch.setattr("app.core.db.Database.value", mock_value)
    with open(FILENAME, "rb") as f:
        response = test_app.post(
            "/api/v0/workflow/results",
            files=[("result_pkl_file", (mock_object_name, f, "application/octet-stream"))],
        )
        d = response.json()
        print(d)
        assert len(d["dispatch_id"]) > 0


def test_put(test_app, monkeypatch):
    async def mock_download(_, filename):
        return b"".join(file_reader())

    async def mock_upload(_, file):
        return {"filename": FILENAME, "path": DIRNAME}

    def mock_value(_, sql: str, key: str = None):
        return (True,)

    mock_object_name = "mocktask"

    monkeypatch.setattr("app.core.api.DataService.download", mock_download)
    monkeypatch.setattr("app.core.api.DataService.upload", mock_upload)
    monkeypatch.setattr("app.core.db.Database.value", mock_value)
    task = {"node_id": 0, "node_name": "subtask", "output": 27}

    response = test_app.put(
        f"/api/v0/workflow/results/{MOCK_DISPATCH_ID}", files={"task": pickle.dumps(task)}
    )

    d = response.json()
    print(response.status_code)
    print(d)
    assert d["response"] == "Task updated successfully"


def test_db_value():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        resultsdb = f.name
    test_db = db.Database(resultsdb)

    sql = f"INSERT INTO results VALUES('{MOCK_DISPATCH_ID}','{FILENAME}','{DIRNAME}')"

    insert = test_db.value(sql)

    sql = "SELECT filename FROM results WHERE dispatch_id=?"
    value = test_db.value(sql, key=MOCK_DISPATCH_ID)

    os.remove(resultsdb)

    assert insert == (True,)
    assert value == (FILENAME,)
